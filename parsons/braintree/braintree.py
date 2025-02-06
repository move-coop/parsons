import logging

import braintree

from parsons.etl.table import Table
from parsons.utilities.check_env import check as check_env

logger = logging.getLogger(__name__)


class ParsonsBraintreeError(Exception):
    pass


class Braintree(object):
    """
    Braintree is a payment processor.
    `Args:`
        merchant_id: str
            Braintree merchant id -- probably a 16-char alphanumeric.
            Not required if ``BRAINTREE_MERCHANT_ID`` env variable is set.
        public_key: str
            Braintree public key -- probably a (different) 16-char alphanumeric.
            Not required if ``BRAINTREE_PUBLIC_KEY`` env variable is set.
        private_key: str
            Braintree private key -- probably a 32-char alphanumeric.
            Not required if ``BRAINTREE_PRIVATE_KEY`` env variable is set.
        timeout: int
            Optionally change the timeout from default of 200 seconds.
            Can also be passed with env var ``BRAINTREE_TIMEOUT``.
        production: bool
            Defaults to True.  If you are testing in a Sandbox,
            set this to False.
    `Returns:`
        Braintree class
    """

    query_types = {
        "dispute": braintree.DisputeSearch,
        "transaction": braintree.TransactionSearch,
        "subscription": braintree.SubscriptionSearch,
    }

    credit_card_fields = [
        "bin",
        "card_type",
        "cardholder_name",
        "commercial",
        "country_of_issuance",
        "customer_location",
        "debit",
        "durbin_regulated",
        "expiration_month",
        "expiration_year",
        "healthcare",
        "image_url",
        "issuing_bank",
        "last_4",
        "payroll",
        "prepaid",
        "product_id",
        "token",
        "venmo_sdk",
    ]

    disbursement_fields = [
        "disbursement_date",  # => disbursement_date column
        "funds_held",
        "settlement_amount",
        "settlement_currency_exchange_rate",
        "settlement_currency_iso_code",
        "success",
    ]

    transaction_fields = [
        "additional_processor_response",
        "amount",
        "avs_error_response_code",
        "avs_postal_code_response_code",
        "avs_street_address_response_code",
        "channel",
        "created_at",
        "currency_iso_code",
        "cvv_response_code",
        "discount_amount",
        "escrow_status",
        "gateway_rejection_reason",
        "id",
        "master_merchant_account_id",
        "merchant_account_id",
        "order_id",
        "payment_instrument_type",
        "plan_id",
        "processor_authorization_code",
        "processor_response_code",
        "processor_response_text",
        "processor_settlement_response_code",
        "processor_settlement_response_text",
        "purchase_order_number",
        "recurring",
        "refund_id",
        "refunded_transaction_id",
        "service_fee_amount",
        "settlement_batch_id",
        "shipping_amount",
        "ships_from_postal_code",
        "status",
        "sub_merchant_account_id",
        "subscription_id",
        "tax_amount",
        "tax_exempt",
        "type",
        "updated_at",
        "voice_referral_number",
    ]

    dispute_fields = [
        "id",
        "amount_disputed",
        "amount_won",
        "case_number",
        "currency_iso_code",
        "kind",
        "merchant_account_id",
        "original_dispute_id",
        "processor_comments",
        "reason",
        "reason_code",
        "reason_description",
        "received_date",
        "reference_number",
        "reply_by_date",
        "status",
        # 'transaction.id', # DOT id -- needs to be special-cased (below)
    ]

    subscription_fields = [
        "add_ons",
        "balance",
        "billing_day_of_month",
        "billing_period_end_date",
        "billing_period_start_date",
        "created_at",
        "current_billing_cycle",
        "days_past_due",
        "description",
        # 'descriptor',  # covered under descriptor_fields
        "discounts",
        "failure_count",
        "first_billing_date",
        "id",
        "merchant_account_id",
        "never_expires",
        "next_bill_amount",
        "next_billing_date",
        "next_billing_period_amount",
        "number_of_billing_cycles",
        "paid_through_date",
        "payment_method_token",
        "plan_id",
        "price",
        "status",
        "status_history",
        # 'transactions', # special-cased
        "trial_duration",
        "trial_duration_unit",
        "trial_period",
        "updated_at",
    ]

    descriptor_fields = ["name", "phone", "url"]

    customer_fields = ["first_name", "last_name", "email"]

    def __init__(
        self,
        merchant_id=None,
        public_key=None,
        private_key=None,
        timeout=None,
        production=True,
    ):
        merchant_id = check_env("BRAINTREE_MERCHANT_ID", merchant_id)
        public_key = check_env("BRAINTREE_PUBLIC_KEY", public_key)
        private_key = check_env("BRAINTREE_PRIVATE_KEY", private_key)
        timeout = check_env("BRAINTREE_TIMEOUT", timeout, optional=True) or 200

        self.gateway = braintree.BraintreeGateway(
            braintree.Configuration(
                environment=(
                    braintree.Environment.Production
                    if production
                    else braintree.Environment.Sandbox
                ),
                merchant_id=merchant_id,
                public_key=public_key,
                private_key=private_key,
                timeout=timeout,
            )
        )

    def get_disputes(self, start_date=None, end_date=None, query_list=None, query_dict=None):
        """
        Get a table of disputes based on query parameters.
        There are three ways to pass query arguments: Pass a start_date and end_date
        together for a date range, or pass a query_list or query_dict argument.

        `Args:`
            start_date: date or str
                Start date of the dispute range. Requires `end_date` arg. e.g. '2020-11-03'
            end_date: date or str
                End date of the dispute range. Requires `start_date` arg. e.g. '2020-11-03'
            query_list: list of braintree.DisputeSearch
                You can use the `braintree.DisputeSearch
                <https://developers.braintreepayments.com/reference/request/dispute/search/python>`_
                to create a manual list of query parameters.
            query_dict: jsonable-dict
                query_dict is basically the same as query_list, except instead of using their API
                objects, you can pass it in pure dictionary form.
                Some examples:
                    .. highlight:: python
                    .. code-block:: python

                      # The start_date/end_date arguments are the same as
                      {"effective_date": {"between": [start_date, end_date]}}
                      # some other examples
                      {"merchant_account_id": {"in_list": [123, 456]}}
                      {"created_at": {"greater_than_or_equal": "2020-03-10"}}

        `Returns:`
            Table Class
        """
        collection = self._get_collection(
            "dispute",
            query_list=query_list,
            query_dict=query_dict,
            default_query=(
                {"effective_date": dict(between=[start_date, end_date])}
                if start_date and end_date
                else None
            ),
        )

        # Iterating on collection.items triggers web requests in batches of 50 records
        # Disputes query api doesn't return the ids -- we can't do anything but iterate
        if not collection.is_success:
            raise ParsonsBraintreeError(f"Braintree dispute query failed: {collection.message}")
        return Table(
            [self._dispute_header()] + [self._dispute_to_row(r) for r in collection.disputes.items]
        )

    def get_subscriptions(
        self,
        table_of_ids=None,
        start_date=None,
        end_date=None,
        query_list=None,
        query_dict=None,
        include_transactions=False,
        just_ids=False,
    ):
        """
        Get a table of subscriptions based on query parameters.
        There are three ways to pass query arguments:
        Pass a disbursement_start_date and disbursement_end_date together
        for a date range, or pass a query_list or query_dict argument.

        `Args:`
            start_date: date or str
                Start date of the subscription range. Requires `end_date` arg.
                e.g. '2020-11-03'
            end_date: date or str
                End date of the subscription range. Requires `start_date` arg.
                e.g. '2020-11-03'
            query_list: list of braintree.SubscriptionSearch
                You can use the `braintree.SubscriptionSearch
                <https://developers.braintreepayments.com/reference/request/subscription/search/python>`_
                to create a manual list of query parameters.
            query_dict: jsonable-dict
                query_dict is basically the same as query_list, except instead of using their API
                objects, you can pass it in pure dictionary form.
                Some examples:
                    .. highlight:: python
                    .. code-block:: python

                      # The start_date/end_date arguments are the same as
                      {"created_at": {"between": [start_date, end_date]}}
                      # some other examples
                      {"merchant_account_id": {"in_list": [123, 456]}}
                      {"created_at": {"greater_than_or_equal": "2020-03-10"}}
            include_transactions: bool
                If this is true, include the full collection of transaction objects.
                Otherwise, just return a list of transaction IDs.
            just_ids: bool
                While querying a list of subscription ids is a single, fast query to Braintree's
                API, getting all data for each subscription is force-paginated at 50-records per
                request. If you just need a count or the list of ids, then set `just_ids=True` and
                it will return a single column with `id` instead of all table columns.
            table_of_ids: Table with an `id` column -- i.e. a table returned from `just_ids=True`
                Subsequently, after calling this with `just_ids`, you can prune/alter the ids table
                and then pass the table back to get the full data.
                These are somewhat-niche use-cases, but occasionally crucial
                when a search result returns 1000s of ids.
        `Returns:`
            Table Class
        """
        collection = self._get_collection(
            "subscription",
            table_of_ids=table_of_ids,
            query_list=query_list,
            query_dict=query_dict,
            default_query=(
                {"created_at": dict(between=[start_date, end_date])}
                if start_date and end_date
                else None
            ),
        )
        query_count = len(collection.ids)
        logger.info(
            f"Braintree subscriptions search resulted in subscriptions count of {query_count}"
        )
        if just_ids:
            return Table([("id",)] + [[item_id] for item_id in collection.ids])

        # Iterating on collection.items triggers web requests in batches of 50 records
        # This can be frustratingly slow :-(
        # Also note: Braintree will push you to their new GraphQL API,
        #   but it, too, paginates with a max of 50 records
        logger.debug("Braintree subscriptions iterating to build subscriptions table")
        return Table(
            [self._subscription_header(include_transactions)]
            + [self._subscription_to_row(include_transactions, r) for r in collection.items]
        )

    def get_transactions(
        self,
        table_of_ids=None,
        disbursement_start_date=None,
        disbursement_end_date=None,
        query_list=None,
        query_dict=None,
        just_ids=False,
    ):
        """
        Get a table of transactions based on query parameters.
        There are three ways to pass query arguments:
        Pass a disbursement_start_date and disbursement_end_date together
        for a date range, or pass a query_list or query_dict argument.

        `Args:`
            disbursement_start_date: date or str
                Start date of the disbursement range. Requires `disbursement_end_date` arg.
                e.g. '2020-11-03'
            disbursement_end_date: date or str
                End date of the disbursement range. Requires `disbursement_start_date` arg.
                e.g. '2020-11-03'
            query_list: list of braintree.TransactionSearch
                You can use the `braintree.TransactionSearch
                <https://developers.braintreepayments.com/reference/request/transaction/search/python>`_
                to create a manual list of query parameters.
            query_dict: jsonable-dict
                query_dict is basically the same as query_list, except instead of using their API
                objects, you can pass it in pure dictionary form.
                Some examples:
                    .. highlight:: python
                    .. code-block:: python

                      # The disbursement_start_date/disbursement_end_date arguments are the same as
                      {"disbursement_date": {"between": [start_date, end_date]}}
                      # some other examples
                      {"merchant_account_id": {"in_list": [123, 456]}}
                      {"created_at": {"greater_than_or_equal": "2020-03-10"}}
            just_ids: bool
                While querying a list of transaction ids is a single, fast query to Braintree's API,
                getting all data for each transaction is force-paginated at 50-records per request.
                If you just need a count or the list of ids, then set `just_ids=True` and
                it will return a single column with `id` instead of all table columns.
            table_of_ids: Table with an `id` column -- i.e. a table returned from `just_ids=True`
                Subsequently, after calling this with `just_ids`, you can prune/alter the ids table
                and then pass the table back to get the full data.
                These are somewhat-niche use-cases, but occasionally crucial
                when a search result returns 1000s of ids.
        `Returns:`
            Table Class
        """
        collection = self._get_collection(
            "transaction",
            table_of_ids=table_of_ids,
            query_list=query_list,
            query_dict=query_dict,
            default_query=(
                {
                    "disbursement_date": dict(
                        between=[disbursement_start_date, disbursement_end_date]
                    )
                }
                if disbursement_start_date and disbursement_end_date
                else None
            ),
        )
        query_count = len(collection.ids)
        logger.info(f"Braintree transactions resulted in transaction count of {query_count}")
        if just_ids:
            return Table([("id",)] + [[item_id] for item_id in collection.ids])

        # Iterating on collection.items triggers web requests in batches of 50 records
        # This can be frustratingly slow :-(
        # Also note: Braintree will push you to their new GraphQL API,
        #   but it, too, paginates with a max of 50 records
        logger.debug("Braintree transactions iterating to build transaction table")
        return Table(
            [self._transaction_header()] + [self._transaction_to_row(r) for r in collection.items]
        )

    def _dispute_header(self):
        return self.dispute_fields + ["transaction_id"]

    def _dispute_to_row(self, collection_item):
        row = [getattr(collection_item, k) for k in self.dispute_fields]
        # the single sub-attribute
        row.append(collection_item.transaction.id)
        return row

    def _transaction_header(self):
        return (
            [f"credit_card_{k}" for k in self.credit_card_fields]
            # annoying exception in column name
            + [
                (f"disbursement_{k}" if k != "disbursement_date" else k)
                for k in self.disbursement_fields
            ]
            + [f"customer_{k}" for k in self.customer_fields]
            + self.transaction_fields
        )

    def _transaction_to_row(self, collection_item):
        return (
            [
                (
                    collection_item.credit_card.get(k)
                    if getattr(collection_item, "credit_card", None)
                    else None
                )
                for k in self.credit_card_fields
            ]
            + [getattr(collection_item.disbursement_details, k) for k in self.disbursement_fields]
            + [getattr(collection_item.customer_details, k) for k in self.customer_fields]
            + [getattr(collection_item, k) for k in self.transaction_fields]
        )

    def _subscription_header(self, include_transactions):
        if include_transactions:
            return (
                [f"descriptor_{k}" for k in self.descriptor_fields]
                + self.subscription_fields
                + ["transactions"]
            )
        else:
            return (
                [f"descriptor_{k}" for k in self.descriptor_fields]
                + self.subscription_fields
                + ["transaction_ids"]
            )

    def _subscription_to_row(self, include_transactions, collection_item):
        if include_transactions:
            return (
                [getattr(collection_item.descriptor, k) for k in self.descriptor_fields]
                + [getattr(collection_item, k) for k in self.subscription_fields]
                + [collection_item.transactions]
            )
        else:
            return (
                [getattr(collection_item.descriptor, k) for k in self.descriptor_fields]
                + [getattr(collection_item, k) for k in self.subscription_fields]
                + [";".join(t.id for t in collection_item.transactions)]
            )

    def _get_collection(
        self,
        query_type,
        table_of_ids=None,
        query_list=None,
        query_dict=None,
        default_query=None,
    ):
        collection_query = None
        collection = None
        if query_list:
            collection_query = query_list
        elif query_dict:
            collection_query = self._get_query_objects(query_type, **query_dict)
        elif default_query:
            collection_query = self._get_query_objects(query_type, **default_query)
        if not collection_query:
            raise ParsonsBraintreeError(
                "You must pass some query parameters: "
                "query_dict, start_date with end_date, or query_list"
            )

        if table_of_ids:
            # We don't need to re-do the query, we can just reconstruct the query object
            collection = self._create_collection(
                query_type, table_of_ids.table.values("id"), collection_query
            )
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
            # Very meta programming here, abstracting braintree library's (dumb?) attribute style
            # Example: braintree.DisputeSearch.effective_date
            # Example: braintree.TransactionSearch.disbursement_date
            queryobj = getattr(self.query_types[query_type], node, None)
            if queryobj:
                for qual, vals in filters.items():  # likely only one, but fine
                    queryobj_qualfunc = getattr(queryobj, qual, None)
                    if not queryobj_qualfunc:
                        raise ParsonsBraintreeError("oh no, that's not a braintree parameter")
                    if not isinstance(vals, list):
                        vals = [vals]
                    queries.append(queryobj_qualfunc(*vals))
            else:
                raise ParsonsBraintreeError("oh no, that's not a braintree parameter")
        return queries

    def _create_collection(self, query_type, ids, queries):
        if (query_type == "transaction") or (query_type == "disbursement"):
            gateway = braintree.TransactionGateway(self.gateway)
            return braintree.ResourceCollection(
                queries,
                {"search_results": {"ids": list(ids), "page_size": 50}},
                method=gateway._TransactionGateway__fetch,
            )
        if query_type == "subscription":
            gateway = braintree.SubscriptionGateway(self.gateway)
            return braintree.ResourceCollection(
                queries,
                {"search_results": {"ids": list(ids), "page_size": 50}},
                method=gateway._SubscriptionGateway__fetch,
            )
