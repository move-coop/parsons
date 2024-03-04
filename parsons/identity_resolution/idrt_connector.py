import logging
import os
from typing import Optional

from idrt.algorithm.utils import download_model, table_from_full_path
from idrt.algorithm import step_1_encode_contacts, step_2_run_search

from parsons.databases.database_connector import DatabaseConnector
from parsons.identity_resolution.idrt_db_adapter import ParsonsDBAdapter

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class IDRT:
    def __init__(
        self,
        db: DatabaseConnector,
        output_schema: Optional[str] = None,
        tokens_table_name: str = "idr_tokens",
        encodings_table_name: str = "idr_out",
        duplicates_table_name: str = "idr_dups",
        enable_progress_bar: bool = True,
    ):
        """Create a new IDRT connector.

        Args:
            db (DatabaseConnector): The database connection you want to use.
                Must support the `upsert` method!
            output_schema (Optional[str], optional): Schema, or database,
                & schema, where intermediate and final output tables will
                be stored. If none is provided, will look in the `OUTPUT_SCHEMA`
                environmental variable. Defaults to None.
                Ex: "my_orgs_contact_data" or "dev.contacts"
            tokens_table_name (str, optional): Name of the table
                in `output_schema` to store tokenizations of contact data.
                Defaults to "idr_tokens".
            encodings_table_name (str, optional): Name of the table
                in `output_schema` to store vector encodings of contacts.
                Defaults to "idr_out".
            duplicates_table_name (str, optional): Name of the table
                in `output_schema` to store the final duplicate evaluation
                results. Defaults to "idr_dups".
            enable_progress_bar (bool, optional): Show the progress bar while
                running models. Recommend set to `False` when running in
                non-standard terminal output environmnets, like Civis platform,
                where it can draw a new progress bar on every line for every
                row it calculates! Defaults to `True`.
        """
        self.db = ParsonsDBAdapter(db)

        self.schema = (
            output_schema if output_schema is not None else os.environ["OUTPUT_SCHEMA"]
        )
        self.tokens_table = table_from_full_path(self.schema + "." + tokens_table_name)
        self.encodings_table = table_from_full_path(
            self.schema + "." + encodings_table_name
        )
        self.duplicates_table = table_from_full_path(
            self.schema + "." + duplicates_table_name
        )
        self.invalid_table = table_from_full_path(self.schema + ".idr_invalid_contacts")
        self.enable_progress_bar = enable_progress_bar

    @staticmethod
    def model_path(filename: str) -> str:
        """Construct the full path to download a model in the case a path was not provided.

        Will download the file to the working directory of the program.

        Args:
            filename (str): Filename of the download file.

        Returns:
            str: Complete path for the download.
        """
        return os.path.join(os.getcwd(), filename)

    def step_1_encode_contacts(
        self,
        data_table_name: Optional[str] = None,
        batch_size: Optional[int] = None,
        limit: Optional[int] = None,
        encoder_url: Optional[str] = None,
        encoder_path: Optional[str] = None,
    ):
        """Step 1 of the IDRT algorithm. Execute before step 2!

        This step downloads the contact data from `data_table_name`, encodes all of the rows,
        and uploads the vector encodings of the contact data into the database. Those vector
        encodings are used by step 2 of the algorithm to identify candidate duplicates.

        The size of the vectors produced for each contact encoding are determined by the encoder
        model used in the algorithm.

        You must supply either `encoder_url` or `encoder_path` to specify where the encoder
        model is located.

        Note: For large sets of data, you will need to run step 1 multiple times to make
        sure that all of your contacts are encoding before step 2 will produce complete
        results. The algorithm caches results appropriately so this will not cause problems
        if you run step 2 against incomplete data. But be aware that you will probably need
        to run step 1 multiple times before step 2 is producing complete results. To check
        this, you can query for the number of primary keys in `data_table_name` that are not
        present in the encodings table (passed into the IDRT class constructor).

        Args:
            batch_size (Optional[int], optional): Number of contacts the model process
                at once. Raising this will increase speed, with diminishing returns
                based on your RAM/VRAM. If your program crashes, try lowering this.
                If none is provided, will look in the `BATCH_SIZE` environmental variable.
                Defaults to 16.
            data_table_name (Optional[str], optional): Full SQL path of the table containing
                formatted contact data to encode. If none is provided, will look in the
                `DATA_TABLE` environmental variable. Defaults to None.
            limit (Optional[int], optional): Number of contacts to process. Limiting will be
                required if you have more contacts than available RAM/VRAM. The lower the limit,
                the more times you will need to run step 1 to encode all of your contacts and
                match your whole database in step 2. If your program crashes, try lowering this.
                If none is provided, will look in the `LIMIT` environmental variable.
                Defaults to 500,000.
            encoder_url (Optional[str], optional): URL where the encoder model can be downloaded.
                If absent, will look in the `ENCODER_URL` environmental variable.
                Defaults to None.
            encoder_path (Optional[str], optional): Path to an existing encoder model file.
                If absent, will look in the `ENCODER_PATH` environmental variable. If no
                `encoder_path` is provided, will download from the provided encoder_url.
                Should be an absolute path. Defaults to None.
        """
        batch_size = (
            batch_size if batch_size is not None else int(os.getenv("BATCH_SIZE", 16))
        )
        data_table = (
            table_from_full_path(data_table_name)
            if data_table_name is not None
            else table_from_full_path(os.environ["DATA_TABLE"])
        )
        limit = limit if limit is not None else int(os.getenv("LIMIT", 500_000))
        encoder_url = (
            encoder_url if encoder_url is not None else os.getenv("ENCODER_URL")
        )
        encoder_path = (
            encoder_path if encoder_path is not None else os.getenv("ENCODER_PATH")
        )

        if encoder_path is None and encoder_url is not None:
            encoder_path = IDRT.model_path("encoder.pt")
            logger.debug(
                f"Downloading encoder model from {encoder_url} to {encoder_path}"
            )
            download_model(encoder_url, encoder_path)
        elif encoder_path is None:
            raise RuntimeError("Must supply encoder_path or encoder_url")

        step_1_encode_contacts(
            self.db,
            batch_size=batch_size,
            data_table=data_table,
            tokens_table=self.tokens_table,
            output_table=self.encodings_table,
            invalid_table=self.invalid_table,
            limit=limit,
            encoder_path=encoder_path,
            enable_progress_bar=self.enable_progress_bar,
        )

    def step_2_run_search(
        self,
        threshold: Optional[float] = None,
        classifier_threshold: Optional[float] = None,
        n_closest: Optional[int] = None,
        batch_size: Optional[int] = None,
        search_pool: Optional[str] = None,
        source_pool: Optional[str] = None,
        n_trees: Optional[int] = None,
        search_k: Optional[int] = None,
        encoder_url: Optional[str] = None,
        encoder_path: Optional[str] = None,
        classifier_url: Optional[str] = None,
        classifier_path: Optional[str] = None,
    ):
        """Step 2 of the IDRT algorithm. Execute after step 1!

        This step uses the work done in step 1 to efficietly identify duplicates for
        contacts that have already been encoded. It takes any vectors that are within
        `threshold` and compares them using the classifier model to produce a
        classification score for that pair. Any pairs that are over `classifier_threshold`
        are considered to be duplicates.

        You must supply either `encoder_url` or `encoder_path` to specify where the encoder
        model is located, and you must supply either `classifier_url` or `classifier_path` to
        specify where the classifier model is located.


        Note: The distance used by the algorithm is the distance under the metric that the
        model was trained with. This might not be standard Euclidean distance. For example,
        the `idrt.CosineMetric` class treats pairs as being within the threshold if the
        distance is _above_ the threshold. When in doubt, do not supply a value for
        `classifier_threshold`, and the model will fall back on the default value stored in
        the classifier model.

        Args:
            threshold (Optional[float], optional): Distance metric threshold to determine
                if two contacts shoudl be evaluated as duplicates. A threshold considering more
                pairs (higher if Euclidean, lower if Cosine) will consider more possible duplicates
                at the cost of performance. See note above. Defaults to None.
            classifier_threshold (Optional[float], optional): Float between 0 - 1.
                If classification score is above `classifier_threshold`, consider
                pairs a duplicate. If None, uses the training value for the model.
                Defaults to None.
            n_closest (Optional[int], optional): The number of closest pairs to evaluate per
                contact. If none is provided, will look in the `N_CLOSEST` environmental variable.
                If none is provided or found, defaults to 2.
            batch_size (Optional[int], optional): Number of contacts the model process
                at once. Raising this will increase speed, with diminishing returns
                based on your RAM/VRAM. If your program crashes, try lowering this.
                If none is provided, will look in the `BATCH_SIZE` environmental variable.
                Defaults to 16.
            search_pool (Optional[str], optional): The pool of contacts to use as possible
                duplicate candidates. If absent, will look in the `SEARCH_POOL` environmental
                variable If none is found, then the algorithm will use all encoded contacts as
                duplicate candidates. Defaults to None.
            source_pool (Optional[str], optional): The pool of contacts to search to find their
                duplicates. If absent, will look in the `SOURCE_POOL` environmental variable.
                If none is found, then the algorithm will search for duplicates of all encoded
                contacts. Defaults to None.
            n_trees (Optional[int], optional): A higher value gives more precision when finding
                duplicate candidates. See https://github.com/spotify/annoy#full-python-api.
                If none is provided, will look in the `N_TREES` environmental variable.
                If none is found, defaults to 10.
            search_k (Optional[int], optional): Configures the `search_k` value in the nearest
                neighbor search. See https://github.com/spotify/annoy#full-python-api.
                If none is provided, will look in the `SEARCH_K` environmental variable.
                If none is found, defaults to -1.
            encoder_url (Optional[str], optional): URL where the encoder model can be downloaded.
                If absent, will look in the `ENCODER_URL` environmental variable.
                Defaults to None.
            encoder_path (Optional[str], optional): Path to an existing encoder model file.
                If absent, will look in the `ENCODER_PATH` environmental variable. If no
                `encoder_path` is provided, will download from the provided encoder_url.
                Should be an absolute path. Defaults to None.
            classifier_url (Optional[str], optional): URL where the classifier model can be
                downloaded. If absent, will look in the `CLASSIFIER_URL` environmental variable.
                Defaults to None.
            classifier_path (Optional[str], optional): Path to an existing classifier model file.
                If absent, will look in the `CLASSIFIER_PATH` environmental variable. If no
                `classifier_path` is provided, will download from the provided classifier_url.
                Should be an absolute path. Defaults to None.
        """
        dup_candidate_table = table_from_full_path(f"{self.schema}.idr_candidates")

        if threshold is None and os.getenv("THRESHOLD"):
            threshold = float(os.environ["THRESHOLD"])

        if classifier_threshold is None and os.getenv("CLASSIFIER_THRESHOLD"):
            classifier_threshold = float(os.environ["CLASSIFIER_THRESHOLD"])

        n_closest = (
            n_closest if n_closest is not None else int(os.getenv("N_CLOSEST", 2))
        )
        n_trees = n_trees if n_trees is not None else int(os.getenv("N_TREES", 10))
        search_k = search_k if search_k is not None else int(os.getenv("SEARCH_K", -1))
        batch_size = (
            batch_size if batch_size is not None else int(os.getenv("BATCH_SIZE", 16))
        )
        search_pool = search_pool or os.getenv("SEARCH_POOL")
        source_pool = source_pool or os.getenv("SOURCE_POOL")

        encoder_url = (
            encoder_url if encoder_url is not None else os.getenv("ENCODER_URL")
        )
        encoder_path = (
            encoder_path if encoder_path is not None else os.getenv("ENCODER_PATH")
        )

        if encoder_path is None and encoder_url is not None:
            encoder_path = IDRT.model_path("encoder.pt")
            logger.debug(
                f"Downloading encoder model from {encoder_url} to {encoder_path}"
            )
            download_model(encoder_url, encoder_path)
        elif encoder_path is None:
            raise RuntimeError("Must supply encoder_path or encoder_url")

        classifier_url = (
            classifier_url
            if classifier_url is not None
            else os.getenv("CLASSIFIER_URL")
        )
        classifier_path = (
            classifier_path
            if classifier_path is not None
            else os.getenv("CLASSIFIER_PATH")
        )

        if classifier_path is None and classifier_url is not None:
            classifier_path = IDRT.model_path("classifier.pt")
            logger.debug("Downloading classifier model")
            download_model(classifier_url, classifier_path)
        elif classifier_path is None:
            raise RuntimeError("Must supply classifier_path or classifier_url")

        step_2_run_search(
            self.db,
            encoder_path=encoder_path,
            classifier_path=classifier_path,
            source_table=self.encodings_table,
            tokens_table=self.tokens_table,
            dup_candidate_table=dup_candidate_table,
            dup_output_table=self.duplicates_table,
            threshold=threshold,
            classifier_threshold=classifier_threshold,
            source_pool=source_pool,
            search_pool=search_pool,
            n_trees=n_trees,
            n_closest=n_closest,
            search_k=search_k,
            batch_size=batch_size,
            enable_progress_bar=self.enable_progress_bar,
        )
