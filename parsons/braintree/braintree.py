import logging

import braintree

from parsons.etl.table import Table
from parsons.utilities.check_env import check as check_env

logger = logging.getLogger(__name__)
# log.info()
# log.debug()

class Braintree(object):

    query_types = {
        'dispute': braintree.DisputeSearch,
        'transaction': braintree.TransactionSearch,
    }

    credit_card_fields = [
        'bin',
        'card_type',
        'cardholder_name',
        'commercial',
        'country_of_issuance',
        'customer_location',
        'debit',
        'durbin_regulated',
        'expiration_month',
        'expiration_year',
        'healthcare',
        'image_url',
        'issuing_bank',
        'last_4',
        'payroll',
        'prepaid',
        'product_id',
        'token',
        'venmo_sdk',
    ]

    disbursement_fields = [
        'disbursement_date',  # => disbursement_date column
        'funds_held',
        'settlement_amount',
        'settlement_currency_exchange_rate',
        'settlement_currency_iso_code',
        'success',
    ]

    transaction_fields = [
        'additional_processor_response',
        'amount',
        'avs_error_response_code',
        'avs_postal_code_response_code',
        'avs_street_address_response_code',
        'channel',
        'created_at',
        'currency_iso_code',
        'cvv_response_code',
        'discount_amount',
        'escrow_status',
        'gateway_rejection_reason',
        'id',
        'master_merchant_account_id',
        'merchant_account_id',
        'order_id',
        'payment_instrument_type',
        'plan_id',
        'processor_authorization_code',
        'processor_response_code',
        'processor_response_text',
        'processor_settlement_response_code',
        'processor_settlement_response_text',
        'purchase_order_number',
        'recurring',
        'refund_id',
        'refunded_transaction_id',
        'service_fee_amount',
        'settlement_batch_id',
        'shipping_amount',
        'ships_from_postal_code',
        'status',
        'sub_merchant_account_id',
        'subscription_id',
        'tax_amount',
        'tax_exempt',
        'type',
        'updated_at',
        'voice_referral_number',
    ]

    dispute_fields = [
        'id',
        'amount_disputed',
        'amount_won',
        'case_number',
        'currency_iso_code',
        'kind',
        'merchant_account_id',
        'original_dispute_id',
        'processor_comments',
        'reason',
        'reason_code',
        'reason_description',
        'received_date',
        'reference_number',
        'reply_by_date',
        'status',
        ### 'transaction.id', # DOT id -- needs to be special-cased (below)
    ]

    def __init__(self, merchant_id=None, public_key=None, private_key=None,
                 timeout=None, production=True):
        merchant_id = check_env('BRAINTREE_MERCHANT_ID', merchant_id)
        public_key = check_env('BRAINTREE_PUBLIC_KEY', public_key)
        private_key = check_env('BRAINTREE_PRIVATE_KEY', private_key)
        timeout = check_env('BRAINTREE_TIMEOUT', timeout, optional=True) or 200

        self.gateway = braintree.BraintreeGateway(
            braintree.Configuration(
                environment=(braintree.Environment.Production if production
                             else braintree.Environment.Sandbox),
                merchant_id=merchant_id,
                public_key=public_key,
                private_key=private_key,
                timeout=200))


    def get_disputes(self,
                     start_date=None, end_date=None,
                     query_list=None,
                     query_dict=None):
        collection = self._get_collection('dispute',
                                          query_list=query_list,
                                          query_dict=query_dict,
                                          default_query=(
                                              {'effective_date': dict(between=[start_date, end_date])}
                                              if start_date and end_date
                                              else None
                                          ))

        # Iterating on collection.items triggers web requests in batches of 50 records
        # Disputes query api doesn't return the ids -- we can't do anything but iterate
        if not collection.is_success:
            raise Exception("Braintree dispute query failed")  # TODO: give more info
        return Table([
            self._dispute_header()
        ] + [self._dispute_to_row(r) for r in collection.disputes.items])

    def get_transactions(self,
                          table_of_ids=None,
                          disbursement_start_date=None, disbursement_end_date=None,
                          query_list=None,
                          query_dict=None,
                          just_ids=False):
        collection = self._get_collection(
            'transaction',
            table_of_ids=table_of_ids,
            query_list=query_list,
            query_dict=query_dict,
            default_query=(
                {'disbursement_date': dict(
                    between=[disbursement_start_date, disbursement_end_date])}
                if disbursement_start_date and disbursement_end_date
                else None
            ))
        query_count = len(collection.ids)
        logger.info(f'Braintree transactions resulted in transaction count of {query_count}')
        if just_ids:
            return Table([('id',)]
                         + [[item_id] for item_id in collection.ids])

        # Iterating on collection.items triggers web requests in batches of 50 records
        # This can be frustratingly slow :-(
        # Also note: Braintree will push you to their new GraphQL API,
        #   but it, too, paginates with a max of 50 records
        logger.debug('Braintree transactions iterating to build transaction table')
        return Table([
            self._transaction_header()
        ] + [self._transaction_to_row(r) for r in collection.items])

    def _dispute_header(self):
        return self.dispute_fields + ['transaction_id']

    def _dispute_to_row(self, collection_item):
        row = [getattr(collection_item, k) for k in self.dispute_fields]
        # the single sub-attribute
        row.append(collection_item.transaction.id)
        return row

    def _transaction_header(self):
        return (
            [f'credit_card_{k}' for k in self.credit_card_fields]
            # annoying exception in column name
            + [(f'disbursement_{k}' if k != 'disbursement_date' else k)
               for k in self.disbursement_fields]
            + self.transaction_fields)

    def _transaction_to_row(self, collection_item):
        return (
            [(collection_item.credit_card.get(k)
              if getattr(collection_item, 'credit_card', None) else None)
             for k in self.credit_card_fields]
            + [getattr(collection_item.disbursement_details, k) for k in self.disbursement_fields]
            + [getattr(collection_item, k) for k in self.transaction_fields])

    def _get_collection(self, query_type,
                        table_of_ids=None,
                        query_list=None,
                        query_dict=None,
                        default_query=None):
        collection_query = None
        collection = None
        if query_list:
            collection_query = query_list
        elif query_dict:
            collection_query = self._get_query_objects(query_type, **query_dict)
        elif default_query:
            collection_query = self._get_query_objects(query_type, **default_query)

        if not collection_query:
            raise Exception(
                "You must pass some query parameters: "
                "query_dict, start_date with end_date, or query_list")

        if table_of_ids:
            # We don't need to re-do the query, we can just reconstruct the query object
            collection = self._create_collection(table_of_ids.table.values('id'), collection_query)
        else:
            collection = getattr(self.gateway, query_type).search(*collection_query)
        return collection

    def _get_query_objects(self, query_type, **queryparams):
        """
        Examples:
        disbursement_date={'between': ['2020-03-20', '2020-03-27']}
        merchant_account_id={'in_list': [123, 456]}
        created_at={'greater_than_or_equal': '2020-03-10'}
        """
        queries = []
        for node, filters in queryparams.items():
            # Very meta; 
            # Example: braintree.DisputeSearch.effective_date
            # Example: braintree.TransactionSearch.disbursement_date
            queryobj = getattr(self.query_types[query_type], node, None)
            if queryobj:
                for qual, vals in filters.items():  # likely only one, but fine
                    queryobj_qualfunc = getattr(queryobj, qual, None)
                    if not queryobj_qualfunc:
                        raise Exception("oh no, that's not a braintree parameter")
                    if not isinstance(vals, list):
                        vals = [vals]
                    queries.append(queryobj_qualfunc(*vals))
            else:
                raise Exception("oh no, that's not a braintree parameter")
        return queries

    def _create_collection(self, ids, queries):
        transaction_gateway = braintree.TransactionGateway(self.gateway)
        return braintree.ResourceCollection(
            queries,
            {'search_results': {'ids': list(ids), 'page_size': 50}},
            method=transaction_gateway._TransactionGateway__fetch)
