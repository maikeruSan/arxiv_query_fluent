import feedparser
import urllib.request
import urllib.parse
import http.client
import time
from datetime import datetime
from arxiv import SortCriterion, SortOrder, Result
from typing import List, Union, Optional, Generator
from enum import Enum
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class Category(Enum):
    """
    Enumeration of valid arXiv categories.

    Categories include subjects from Computer Science, Economics, Electrical Engineering, Mathematics,
    Physics, Quantitative Biology, Quantitative Finance, and Statistics.
    """

    CS_AI = "cs.AI"
    CS_AR = "cs.AR"
    CS_CC = "cs.CC"
    CS_CE = "cs.CE"
    CS_CG = "cs.CG"
    CS_CL = "cs.CL"
    CS_CR = "cs.CR"
    CS_CV = "cs.CV"
    CS_CY = "cs.CY"
    CS_DB = "cs.DB"
    CS_DC = "cs.DC"
    CS_DL = "cs.DL"
    CS_DM = "cs.DM"
    CS_DS = "cs.DS"
    CS_ET = "cs.ET"
    CS_FL = "cs.FL"
    CS_GL = "cs.GL"
    CS_GR = "cs.GR"
    CS_GT = "cs.GT"
    CS_HC = "cs.HC"
    CS_IR = "cs.IR"
    CS_IT = "cs.IT"
    CS_LG = "cs.LG"
    CS_LO = "cs.LO"
    CS_MA = "cs.MA"
    CS_MM = "cs.MM"
    CS_MS = "cs.MS"
    CS_NA = "cs.NA"  # alias for math.NA
    CS_NE = "cs.NE"
    CS_NI = "cs.NI"
    CS_OH = "cs.OH"
    CS_OS = "cs.OS"
    CS_PF = "cs.PF"
    CS_PL = "cs.PL"
    CS_RO = "cs.RO"
    CS_SC = "cs.SC"
    CS_SD = "cs.SD"
    CS_SE = "cs.SE"
    CS_SI = "cs.SI"
    CS_SY = "cs.SY"

    # --- Economics ---
    ECON_EM = "econ.EM"
    ECON_GN = "econ.GN"
    ECON_TH = "econ.TH"

    # --- Electrical Engineering and Systems Science ---
    EESS_AS = "eess.AS"
    EESS_IV = "eess.IV"
    EESS_SP = "eess.SP"
    EESS_SY = "eess.SY"

    # --- Mathematics ---
    MATH_AC = "math.AC"
    MATH_AG = "math.AG"
    MATH_AP = "math.AP"
    MATH_AT = "math.AT"
    MATH_CA = "math.CA"
    MATH_CO = "math.CO"
    MATH_CT = "math.CT"
    MATH_CV = "math.CV"
    MATH_DG = "math.DG"
    MATH_DS = "math.DS"
    MATH_FA = "math.FA"
    MATH_GM = "math.GM"
    MATH_GN = "math.GN"
    MATH_GR = "math.GR"
    MATH_GT = "math.GT"
    MATH_HO = "math.HO"
    MATH_IT = "math.IT"
    MATH_KT = "math.KT"
    MATH_LO = "math.LO"
    MATH_MG = "math.MG"
    MATH_MP = "math.MP"
    MATH_NA = "math.NA"
    MATH_NT = "math.NT"
    MATH_OA = "math.OA"
    MATH_OC = "math.OC"
    MATH_PR = "math.PR"
    MATH_QA = "math.QA"
    MATH_RA = "math.RA"
    MATH_RT = "math.RT"
    MATH_SG = "math.SG"
    MATH_SP = "math.SP"
    MATH_ST = "math.ST"

    # --- Physics ---
    # Astrophysics
    ASTRO_PH_CO = "astro-ph.CO"
    ASTRO_PH_EP = "astro-ph.EP"
    ASTRO_PH_GA = "astro-ph.GA"
    ASTRO_PH_HE = "astro-ph.HE"
    ASTRO_PH_IM = "astro-ph.IM"
    ASTRO_PH_SR = "astro-ph.SR"

    # Condensed Matter
    COND_MAT_DIS_NN = "cond-mat.dis-nn"
    COND_MAT_MES_HALL = "cond-mat.mes-hall"
    COND_MAT_MTRL_SCI = "cond-mat.mtrl-sci"
    COND_MAT_OTHER = "cond-mat.other"
    COND_MAT_QUANT_GAS = "cond-mat.quant-gas"
    COND_MAT_SOFT = "cond-mat.soft"
    COND_MAT_STAT_MECH = "cond-mat.stat-mech"
    COND_MAT_STR_EL = "cond-mat.str-el"
    COND_MAT_SUPR_CON = "cond-mat.supr-con"

    # General Relativity and Quantum Cosmology
    GR_QC = "gr-qc"

    # High Energy Physics - Experiment
    HEP_EX = "hep-ex"

    # High Energy Physics - Lattice
    HEP_LAT = "hep-lat"

    # High Energy Physics - Phenomenology
    HEP_PH = "hep-ph"

    # High Energy Physics - Theory
    HEP_TH = "hep-th"

    # Mathematical Physics (alias for math-ph)
    MATH_PH = "math-ph"

    # Nonlinear Sciences
    NLIN_AO = "nlin.AO"
    NLIN_CD = "nlin.CD"
    NLIN_CG = "nlin.CG"
    NLIN_PS = "nlin.PS"
    NLIN_SI = "nlin.SI"

    # Nuclear Experiment
    NUCL_EX = "nucl-ex"

    # Nuclear Theory
    NUCL_TH = "nucl-th"

    # Other Physics
    PHYS_ACC_PH = "physics.acc-ph"
    PHYS_AO_PH = "physics.ao-ph"
    PHYS_APP_PH = "physics.app-ph"
    PHYS_ATM_CLUS = "physics.atm-clus"
    PHYS_ATOM_PH = "physics.atom-ph"
    PHYS_BIO_PH = "physics.bio-ph"
    PHYS_CHEM_PH = "physics.chem-ph"
    PHYS_CLASS_PH = "physics.class-ph"
    PHYS_COMP_PH = "physics.comp-ph"
    PHYS_DATA_AN = "physics.data-an"
    PHYS_ED_PH = "physics.ed-ph"
    PHYS_FLU_DYN = "physics.flu-dyn"
    PHYS_GEN_PH = "physics.gen-ph"
    PHYS_GEO_PH = "physics.geo-ph"
    PHYS_HIST_PH = "physics.hist-ph"
    PHYS_INS_DET = "physics.ins-det"
    PHYS_MED_PH = "physics.med-ph"
    PHYS_OPTICS = "physics.optics"
    PHYS_PLASM_PH = "physics.plasm-ph"
    PHYS_POP_PH = "physics.pop-ph"
    PHYS_SOC_PH = "physics.soc-ph"
    PHYS_SPACE_PH = "physics.space-ph"

    # Quantum Physics
    QUANT_PH = "quant-ph"

    # --- Quantitative Biology ---
    QBIO_BM = "q-bio.BM"
    QBIO_CB = "q-bio.CB"
    QBIO_GN = "q-bio.GN"
    QBIO_MN = "q-bio.MN"
    QBIO_NC = "q-bio.NC"
    QBIO_OT = "q-bio.OT"
    QBIO_PE = "q-bio.PE"
    QBIO_QM = "q-bio.QM"
    QBIO_SC = "q-bio.SC"
    QBIO_TO = "q-bio.TO"

    # --- Quantitative Finance ---
    QFIN_CP = "q-fin.CP"
    QFIN_EC = "q-fin.EC"
    QFIN_GN = "q-fin.GN"
    QFIN_MF = "q-fin.MF"
    QFIN_PM = "q-fin.PM"
    QFIN_PR = "q-fin.PR"
    QFIN_RM = "q-fin.RM"
    QFIN_ST = "q-fin.ST"
    QFIN_TR = "q-fin.TR"

    # --- Statistics ---
    STAT_AP = "stat.AP"
    STAT_CO = "stat.CO"
    STAT_ME = "stat.ME"
    STAT_ML = "stat.ML"
    STAT_OT = "stat.OT"
    STAT_TH = "stat.TH"


class Field(Enum):
    """
    Enumeration of arXiv query fields.

    These fields represent the searchable components of an arXiv entry.
    """

    title = "ti"
    author = "au"
    abstract = "abs"
    comment = "co"
    journal_ref = "jr"
    category = "cat"
    all = "all"
    id = "id"
    submitted_date = "submittedDate"
    rn = "rn"


class Opt(Enum):
    """
    Enumeration of Boolean operators for combining query conditions.
    """

    And = "AND"
    Or = "OR"
    And_Not = "ANDNOT"


class InvalidDateFormatError(Exception):
    """
    Exception raised when a date string does not conform to the expected format.

    Expected formats are YYYYMMDD or YYYYMMDDTTTT.
    """

    pass


class InvalidCategoryError(Exception):
    """
    Exception raised when an invalid category value is provided.

    The category must be one of the predefined Category enum values or a matching string.
    """

    pass


class PrependOperatorError(Exception):
    """
    Exception raised when a Boolean operator is required but missing or of incorrect type.
    """

    pass


class DateRange:
    """
    Class for representing and validating a date range for arXiv API queries.

    Dates should be provided in YYYYMMDD or YYYYMMDDTTTT format. If the time component is missing,
    it is automatically appended (0000 for start dates and 2359 for end dates).

    Example:
        >>> dr = DateRange("20240101", "20241231")
        >>> print(dr)
        [202401010000 TO 202412312359]
    """

    def __init__(self, start: str, end: str):
        """
        Initialize a DateRange with the specified start and end dates.

        Args:
            start (str): Start date in YYYYMMDD or YYYYMMDDTTTT format.
            end (str): End date in YYYYMMDD or YYYYMMDDTTTT format.

        Raises:
            ValueError: If either date format is invalid or if the start date is later than the end date.
        """
        self._validate_date_format(start, "start")
        self._validate_date_format(end, "end")

        # Normalize dates by adding time if needed
        self.start = self._normalize_date(start, is_start=True)
        self.end = self._normalize_date(end, is_start=False)

        # Validate chronological order
        if int(self.start) > int(self.end):
            raise InvalidDateFormatError(f"Start date ({start}) must be earlier than or equal to end date ({end})")

    @staticmethod
    def _validate_date_format(date: str, date_type: str) -> None:
        """
        Validate the date format.

        Args:
            date (str): The date string to validate.
            date_type (str): Indicates whether this is the 'start' or 'end' date for error messages.

        Raises:
            ValueError: If the date format does not match YYYYMMDD or YYYYMMDDTTTT.
        """
        if len(date) == 8:
            date_format = "%Y%m%d"
        elif len(date) == 12:
            date_format = "%Y%m%d%H%M"
        else:
            raise InvalidDateFormatError(f"Invalid {date_type} date format: {date}. Expected format: YYYYMMDD or YYYYMMDDHHMM")

        try:
            datetime.strptime(date, date_format)
        except ValueError as e:
            raise InvalidDateFormatError(f"Invalid {date_type} date: {date} is not a valid date") from e

    @staticmethod
    def _normalize_date(date: str, is_start: bool) -> str:
        """
        Normalize a date string by appending a time component if missing.

        Args:
            date (str): The date string to normalize.
            is_start (bool): True if this is a start date (append '0000'); False if an end date (append '2359').

        Returns:
            str: The normalized date string in YYYYMMDDTTTT format.
        """
        if len(date) == 8:  # YYYYMMDD format
            return date + ("0000" if is_start else "2359")
        return date  # Already in YYYYMMDDTTTT format

    def __str__(self) -> str:
        """
        Convert the DateRange to a string formatted for arXiv API queries.

        Returns:
            str: The date range in the format "[YYYYMMDDTTTT TO YYYYMMDDTTTT]".
        """
        return f"[{self.start} TO {self.end}]"


class Entry(Result):
    """
    A wrapper subclass of the Result class from arxiv.py.

    This class is intended to extend or customize the functionality of the
    original Result class. For more details on the base implementation, please refer to:
    https://github.com/lukasschwab/arxiv.py/blob/master/arxiv/__init__.py
    """

    pass


@dataclass
class FeedResults:
    """
    Data class that encapsulates the results returned from an arXiv API query.

    This class holds the list of individual arXiv query result entries along with associated pagination details.

    Attributes:
        entrys (List[Entry]): A list of arXiv query result entries.
        total_entries_of_query (int): The total number of entries available for the query.
        startIndex (int): The index of the first result in the current page (0-based).
        maxEntryPerPage (int): The maximum number of entries per page as specified in the query.
    """

    entrys: List[Entry]
    total_entries_of_query: int
    startIndex: int
    maxEntryPerPage: int

    def download_pdf(self, identifier: str, dirpath: str, filename: Optional[str] = None) -> Optional[str]:
        """
        Download the PDF file for a specific arXiv entry identified by its short identifier.

        This method iterates through the list of entries and checks if the short identifier of an entry
        matches the provided Identifier. When a match is found, it attempts to download the PDF file for that entry.
        The downloaded PDF will be saved in the specified directory with either a custom filename (if provided)
        or a default filename derived from the arXiv identifier.

        Args:
            Identifier (str): The short arXiv identifier for the entry (as returned by get_short_id()).
            dirpath (str): The directory path where the PDF should be saved.
            filename (Optional[str]): A custom filename for the saved PDF. If not provided, the identifier is used
                                      to generate a filename in the format '<Identifier>.pdf'.

        Returns:
            Optional[str]: The file path of the downloaded PDF if successful; otherwise, None.
        """
        # Iterate over all entries to find the one matching the provided identifier.
        for entry in self.entrys:
            # Check if the entry's short identifier matches the provided Identifier.
            if entry.get_short_id() == identifier:
                # Determine the filename: use the provided filename if available,
                # otherwise, default to '<Identifier>.pdf'.
                fn = filename if filename is not None else f"{identifier}.pdf"
                # Attempt to download the PDF file and return the resulting file path.
                return entry.download_pdf(dirpath, fn)

        # If no matching entry is found, return None.
        return f"Identifier:{identifier} no found in the current entries"

    def current_page(self) -> int:
        return self.startIndex // self.maxEntryPerPage + 1

    def total_page_of_query(self) -> int:
        return (self.total_entries_of_query + self.maxEntryPerPage - 1) // self.maxEntryPerPage

    def show(self, top_n: Optional[int] = None, abstract_shown: int = 200) -> None:
        """
        Display detailed information of the arXiv query results on the console.

        This method prints the results in a formatted manner including pagination info,
        entry index, title, arXiv identifier, authors, publication date, PDF link, and
        a truncated abstract.

        Args:
            top_n (Optional[int]): The maximum number of entries to display. If None, all entries are displayed.
                                   If top_n is 0, nothing is displayed.
            abstract_shown (int): The maximum number of characters to show for each abstract.
                                  If the abstract length exceeds this number, it is truncated with '...'.
        """
        # If top_n is 0, do not display any entries.
        if top_n == 0:
            return None
        # If size of entrys is zero ..
        if len(self.entrys) == 0:
            print("The entries(results) is empty")
            return None

        # Determine the number of entries to display.
        show_n = min(top_n, len(self.entrys)) if top_n is not None else len(self.entrys)

        # Calculate the starting and ending indices for the current page display.
        e_start = self.startIndex + 1
        e_end = self.startIndex + show_n

        # Calculate the total number of entries available on this page.
        last_page_n = self.startIndex + len(self.entrys)

        # Print pagination and entry range information.
        print(f"Entries: {e_start}-{e_end}/({last_page_n}) | Pages: {self.current_page()} / {self.total_page_of_query()}")
        print("───────────────────────────────────────────")

        # Iterate over each entry and display detailed information.
        for i, entry in enumerate(self.entrys, 1):
            # Retrieve PDF link if available.
            pdf_link = next((str(l.href) for l in entry.links if l.title == "pdf"), None)
            if pdf_link is None:
                logger.warning(f"No PDF link found for entry {i}: {entry.title}")

            # Display entry information.
            print(f"Entry: #{self.startIndex + i}")
            print(f"Title: {entry.title} | arXiv Identifier: {entry.get_short_id()}")
            print(f"Authors: {', '.join(a.name for a in entry.authors)}")
            print(f"Published Date: {entry.published}")
            print(f"PDF Link: {pdf_link if pdf_link else 'No PDF link available.'}")

            # Display truncated abstract if applicable.
            if abstract_shown > 0:
                print(f"Abstract:\n{entry.summary[:abstract_shown]}{'...' if len(entry.summary) > abstract_shown else ''}")

            print("───────────────────────────────────────────")

            # Stop after displaying top_n entries if top_n is specified.
            if top_n is not None and i >= top_n:
                break

    def __len__(self) -> int:
        return len(self.entrys)

    def __str__(self) -> str:
        return f"Page Entries: {self.startIndex+1}-{self.startIndex+len(self.entrys)} | Total Entries : {self.total_entries_of_query} | Pages: {self.current_page()} / {self.total_page_of_query()}"

    def desc(self) -> None:
        print(self.__str__())

    def get_list(self) -> str:
        """
        Generate and return a formatted string representing the arXiv feed results.

        For each entry in the feed, this method extracts:
          - The publication date, formatted as 'YYYY-MM-DD'. If the publication date is a datetime object,
            it is directly formatted. If it is a string, an attempt is made to parse it using datetime.fromisoformat;
            if parsing fails, the original value is used.
          - The title of the entry.
          - The authors of the entry, concatenated with commas.

        Each entry is represented on a separate line in the following format:
            [YYYY-MM-DD] [Title] [Author1, Author2, ...]

        Returns:
            str: A formatted string containing all entries from the feed.
        """
        result_str = ""
        for entry in self.entrys:
            # Determine the publication date:
            # - If entry.published is a datetime object, format it directly.
            # - Otherwise, try to parse it with fromisoformat; if that fails, use the original value.
            if isinstance(entry.published, datetime):
                published_date = entry.published.strftime("%Y-%m-%d")
            else:
                try:
                    dt = datetime.fromisoformat(entry.published)
                    published_date = dt.strftime("%Y-%m-%d")
                except Exception:
                    published_date = entry.published
            # Append the formatted entry information to the result string.
            result_str += f"[{published_date}] [{entry.title}] [{','.join(a.name for a in entry.authors)}]\n"
        return result_str

    def list(self) -> None:
        print(self.get_list())


class Query:
    """
    Builder class for constructing and executing arXiv API queries.

    This class provides methods to add individual query conditions or grouped conditions,
    build the complete query string, and execute the query to retrieve paginated results.
    """

    def __init__(
        self,
        base_url: str = "http://export.arxiv.org/api/query?",
        max_entries_per_pager: int = 50,
        sortBy: SortCriterion = SortCriterion.SubmittedDate,
        sortOrder: SortOrder = SortOrder.Descending,
    ):
        """
        Initialize a Query instance with configuration for the arXiv API.

        Args:
            base_url (str): The base URL for the arXiv API.
            max_entries_per_pager (int): Maximum number of (entries)results to return per page.
            sortBy (SortCriterion): The field by which to sort the results.
            sortOrder (SortOrder): The order in which to sort the results.
        """
        self.max_results = max_entries_per_pager
        self.sortBy = sortBy
        self.sortOrder = sortOrder
        self.queries: List[str] = []
        self.base_url = base_url

    def _prepend_boolean_operator(self, query: str, boolean_operator: Optional[Opt]) -> str:
        """
        Prepend a Boolean operator to a query fragment if the query already contains conditions.

        Args:
            query (str): The query fragment to which the Boolean operator may be prepended.
            boolean_operator (Optional[Opt]): The Boolean operator to use; must be provided if there are existing conditions.

        Returns:
            str: The query fragment with the Boolean operator prepended if required.

        Raises:
            PrependOperatorError: If a Boolean operator is required but not provided or of an incorrect type.
        """
        if self.queries:
            if boolean_operator is None:
                raise PrependOperatorError("Boolean operator is required when adding multiple queries")
            if not isinstance(boolean_operator, Opt):
                raise PrependOperatorError(f"Boolean operator must be a BooleanOperator enum, got {type(boolean_operator)}")
            return f"{boolean_operator.value} {query}"
        return query

    def add_group(self, arxiv_query: "Query", boolean_operator: Optional[Opt] = None) -> "Query":
        """
        Add a grouped query by wrapping another Query's search query in parentheses.

        Args:
            arxiv_query (Query): A Query instance whose search_query() returns a query fragment.
            boolean_operator (Optional[Opt]): The Boolean operator to combine this group with existing queries.
                                              Required if there are existing queries.

        Returns:
            Query: Self for method chaining.
        """
        query = f"({arxiv_query.search_query()})"
        query = self._prepend_boolean_operator(query, boolean_operator)
        self.queries.append(query)
        return self

    def add(
        self,
        field: Field,
        value: Union[str, DateRange, Category],
        boolean_operator: Optional[Opt] = None,
    ) -> "Query":
        """
        Add a new query condition to the query string.

        Args:
            field (Field): The field of the arXiv entry to query.
            value (Union[str, DateRange, Category]): The value to search for. For:
                - submitted_date: a DateRange instance must be provided.
                - category: a Category enum or matching string must be provided.
                - Other fields: a string is expected.
            boolean_operator (Optional[Opt]): The Boolean operator to combine with existing queries;
                                              required if adding subsequent conditions.

        Returns:
            Query: Self for method chaining.

        Raises:
            ValueError: If the provided field or value type is invalid.
        """
        if not isinstance(field, Field):
            raise ValueError(f"Field must be a Field enum, got {type(field)}")

        formatted_value = self._format_query_value(field, value)
        query = f"{field.value}:{formatted_value}"
        query = self._prepend_boolean_operator(query, boolean_operator)
        self.queries.append(query)
        return self

    def _format_query_value(self, field: Field, value: Union[str, DateRange, Category]) -> str:
        """
        Format the value for a query condition based on the field type.

        Args:
            field (Field): The field to query.
            value (Union[str, DateRange, Category]): The value to format.

        Returns:
            str: The formatted value as a string suitable for the arXiv API query.

        Raises:
            ValueError: If the value type is invalid for the specified field.
        """
        if field == Field.submitted_date:
            if isinstance(value, DateRange):
                return str(value)
            raise ValueError(f"Submitted date must be a DateRange object, got {type(value)}")

        if field == Field.category:
            if isinstance(value, (str, Category)):
                return f'"{self._validate_category(value)}"'
            raise ValueError(f"Category value must be a string or CATEGORY enum, got {type(value)}")

        if isinstance(value, str):
            return f'"{value}"'

        raise ValueError(f"Invalid value type for field {field.value}: {type(value)}")

    def search_query(self) -> str:
        """
        Build and return the complete query string from all added conditions.

        Returns:
            str: The full query string formatted for the arXiv API.
        """
        return " ".join(self.queries)

    def get(self, page: int = 1, search_query: Optional[str] = None) -> Optional[FeedResults]:
        """
        Execute the query and retrieve a page of results from the arXiv API.

        Args:
            page (int): The page number to retrieve (starting from 1).
            search_query (Optional[str]): A custom search query string; if not provided, the built query string is used.

        Returns:
            FeedResults: An object containing the parsed results and pagination information.
        """
        # Use the default search query if none is provided.
        if search_query is None:
            search_query = self.search_query()
        else:
            return None

        # Calculate the starting index for the results.
        start = (page - 1) * self.max_results

        return Query.http_get(
            base_url=self.base_url, search_query=search_query, max_results=self.max_results, sortBy=self.sortBy, sortOrder=self.sortOrder, start=start
        )

    def api_url(self):
        return Query._build_arxiv_url(self.base_url, self.search_query(), self.max_results, self.sortBy, self.sortOrder, 0)

    def paginated_results(self, max_pages: Optional[int] = None) -> Generator[FeedResults, None, None]:
        """
        Generator function that yields paginated results from an arXiv Query object.

        This function calls the query's get() method repeatedly to obtain batches of results.
        It will yield a FeedResults object for each page until no more results are available or
        the specified maximum number of pages is reached.

        Args:
            max_pages (Optional[int]): The maximum number of pages to process. If None, process all pages.

        Yields:
            FeedResults: The results for each page.
        """
        page = 1
        while True:
            retry_attempt = 0
            results = None
            while retry_attempt < 10:
                results = self.get(page=page)
                # If results is None or contains no entries, retry
                if results is None or not results.entrys:
                    retry_attempt += 1
                    time.sleep(3)
                    continue
                # If not on the last page but the number of entries is less than self.max_results, retry
                if results.startIndex + results.maxEntryPerPage < results.total_entries_of_query and len(results.entrys) < self.max_results:
                    retry_attempt += 1
                    time.sleep(3)
                    continue
                # Otherwise, accept the results
                break
            if retry_attempt >= 10:
                raise Exception(f"Failed to fetch page {page} from arXiv API after 10 attempts.")

            yield results

            if max_pages is not None and page >= max_pages:
                break

            if results.startIndex + results.maxEntryPerPage >= results.total_entries_of_query:
                break

            page += 1
            time.sleep(1.5)

    @staticmethod
    def http_get(
        base_url: str,
        search_query: str,
        max_results: int = 5,
        sortBy: SortCriterion = SortCriterion.SubmittedDate,
        sortOrder: SortOrder = SortOrder.Descending,
        start: int = 0,
    ) -> FeedResults:
        """
        Perform an HTTP GET request to the arXiv API and parse the response.

        Args:
            base_url (str): The base URL for the arXiv API.
            search_query (str): The query string to be sent.
            max_results (int): Maximum number of results to retrieve.
            sortBy (SortCriterion): The field to sort results by.
            sortOrder (SortOrder): The order in which to sort the results.
            start (int): The starting index for the results (0-based).

        Returns:
            FeedResults: An object containing the parsed feed results and pagination information.

        Raises:
            http.client.RemoteDisconnected: If the remote end closes the connection without response.
        """
        url = Query._build_arxiv_url(base_url, search_query, max_results, sortBy, sortOrder, start)
        logger.debug(f"Arxiv API Request URL: {url}")

        try:
            response = urllib.request.urlopen(url).read()
        except http.client.RemoteDisconnected as e:
            logger.error(f"Remote end closed connection without response for URL: {url}")
            raise e
        return Query._parse_feed_response(response)

    @staticmethod
    def _build_arxiv_url(
        base_url: str,
        search_query: str,
        max_results: int,
        sortBy: SortCriterion,
        sortOrder: SortOrder,
        start: int,
    ) -> str:
        """
        Construct the full URL for an arXiv API query.

        Args:
            base_url (str): The base URL for the API.
            search_query (str): The search query string.
            max_results (int): Maximum number of results to return.
            sortBy (SortCriterion): The field to sort by.
            sortOrder (SortOrder): The order in which to sort the results.
            start (int): The starting index for results (0-based).

        Returns:
            str: The complete URL with encoded query parameters.
        """
        params = {
            "search_query": search_query,
            "max_results": max_results,
            "sortBy": sortBy.value,
            "sortOrder": sortOrder.value,
            "start": start,
        }
        query_string = urllib.parse.urlencode(params)
        return base_url + query_string

    @staticmethod
    def _parse_feed_response(response: bytes) -> FeedResults:
        """
        Parse the raw response from the arXiv API using feedparser.

        Args:
            response (bytes): The raw API response in bytes.

        Returns:
            FeedResults: An object containing the list of results and pagination data.
        """
        feed = feedparser.parse(response)

        total_results_of_query = int(getattr(feed.feed, "opensearch_totalresults", -1))
        start_index = int(getattr(feed.feed, "opensearch_startindex", -1))
        items_per_page = int(getattr(feed.feed, "opensearch_itemsperpage", -1))

        entries: List[Result] = [Result._from_feed_entry(entry) for entry in feed.entries]

        return FeedResults(entries, total_results_of_query, start_index, items_per_page)

    @staticmethod
    def _validate_category(value: Union[str, Category]) -> str:
        """
        Validate that the given category is valid.

        Args:
            value (Union[str, Category]): The category value to validate.

        Returns:
            str: The validated category string.

        Raises:
            InvalidCategoryError: If the category is not a valid Category enum member or string.
        """
        if isinstance(value, Category):
            return value.value
        elif isinstance(value, str) and value in {cat.value for cat in Category}:
            return value
        else:
            raise InvalidCategoryError(f"Invalid category: '{value}'. Use a valid CATEGORY enum value from CATEGORY.")
