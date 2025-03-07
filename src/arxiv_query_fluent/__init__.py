import feedparser
import urllib.request
import re
from arxiv import SortCriterion, SortOrder, Result
from typing import List, Union, Optional
from enum import Enum
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class Category(Enum):
    # --- Computer Science ---
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
    """Enum for arXiv query fields."""

    title = "ti"
    author = "au"
    abstract = "abs"
    comment = "co"
    journal_ref = "jr"
    category = "cat"
    all = "all"
    id = "id"
    sumbitted_date = "submittedDate"


class Opt(Enum):
    """Enum for Boolean operators."""

    And = "AND"
    Or = "OR"
    And_Not = "ANDNOT"


class InvalidDateFormatError(Exception):
    """Custom exception for invalid submittedDate format."""

    pass


class InvalidCategoryError(Exception):
    """Custom exception for invalid category selection."""

    pass


class DateRange:
    """Class for handling date ranges in arXiv API queries."""

    def __init__(self, start: str, end: str):
        """Initialize a date range with start and end dates.

        Args:
            start (str): Start date in YYYYMMDD or YYYYMMDDTTTT format
            end (str): End date in YYYYMMDD or YYYYMMDDTTTT format

        Raises:
            ValueError: If dates are invalid or start date is after end date
        """
        self._validate_date_format(start, "start")
        self._validate_date_format(end, "end")

        # Normalize dates by adding time if needed
        self.start = self._normalize_date(start, is_start=True)
        self.end = self._normalize_date(end, is_start=False)

        # Validate chronological order
        if int(self.start) > int(self.end):
            raise ValueError(f"Start date ({start}) must be earlier than or equal to end date ({end})")

    @staticmethod
    def _validate_date_format(date: str, date_type: str) -> None:
        """Validate the date format.

        Args:
            date (str): Date string to validate
            date_type (str): Type of date ('start' or 'end') for error messages

        Raises:
            ValueError: If date format is invalid
        """
        if not re.match(r"^\d{8}(\d{4})?$", date):
            raise ValueError(f"Invalid {date_type} date format: {date}. " "Expected format: YYYYMMDD or YYYYMMDDTTTT")

    @staticmethod
    def _normalize_date(date: str, is_start: bool) -> str:
        """Normalize date by adding time if needed.

        Args:
            date (str): Date string to normalize
            is_start (bool): True if this is a start date, False if end date

        Returns:
            str: Normalized date in YYYYMMDDTTTT format
        """
        if len(date) == 8:  # YYYYMMDD format
            return date + ("0000" if is_start else "2359")
        return date  # Already in YYYYMMDDTTTT format

    def __str__(self) -> str:
        """Convert date range to arXiv API query format.

        Returns:
            str: Date range in format [YYYYMMDDTTTT TO YYYYMMDDTTTT]
        """
        return f"[{self.start} TO {self.end}]"


@dataclass
class FeedResults:
    entrys: List[Result]
    totalResults: int
    startIndex: int
    itemsPerPage: int

    def __str__(self) -> str:
        tostr: str = ""
        for entry in self.entrys:
            tostr = tostr + (f"[{entry.published}]:[{entry.title}]:[{','.join([a.name for a in entry.authors])}]") + "\n"

        return tostr


class Query:
    """Builder class for constructing arXiv API query strings."""

    def __init__(
        self,
        base_url: str = "http://export.arxiv.org/api/query?",
        max_results_per_paer: int = 10,
        sortBy: SortOrder = SortCriterion.SubmittedDate,
        sortOrder: SortOrder = SortOrder.Descending,
    ):
        self.max_results = max_results_per_paer
        self.sortBy = sortBy
        self.sortOrder = sortOrder
        self.queries: List[str] = []
        self.base_url = base_url

    def add_group(self, arxiv_query: "Query", boolean_operator: Optional[Opt] = None) -> "Query":
        query: str = f"({arxiv_query.search_query()})"
        if len(self.queries) > 0:
            if boolean_operator is None:
                raise ValueError("Boolean operator is required when adding multiple queries")
            if not isinstance(boolean_operator, Opt):
                raise ValueError(f"Boolean operator must be a BooleanOperator enum, got {type(boolean_operator)}")
            query = f"{boolean_operator.value} {query}"

        self.queries.append(query)
        return self

    def add(
        self,
        field: Field,
        value: Union[str, DateRange, Category],
        boolean_operator: Optional[Opt] = None,
    ) -> "Query":
        """
        Add a query to the query string.

        Args:
            field (SubCategory): The field to query (from SubCategory Enum).
            value (Union[str, DateRange, CATEGORY]): The value to search for.
                - For SUBMITTED_DATE: Use DateRange object
                - For CATEGORY: Use CATEGORY enum
                - For others: Use string
            boolean_operator (Optional[BooleanOperator]): Boolean operator to combine queries. Required for second and subsequent queries.

        Returns:
            Builder: The QueryStringBuilder instance for method chaining.

        Raises:
            ValueError: If field or value types are invalid.
            ValueError: If submitted date format is invalid.
            ValueError: If boolean operator is missing for subsequent queries.
        """
        if not isinstance(field, Field):
            raise ValueError(f"Field must be a SubCategory enum, got {type(field)}")

        formatted_value = self._format_query_value(field, value)

        query = f"{field.value}:{formatted_value}"
        if len(self.queries) > 0:
            if boolean_operator is None:
                raise ValueError("Boolean operator is required when adding multiple queries")
            if not isinstance(boolean_operator, Opt):
                raise ValueError(f"Boolean operator must be a BooleanOperator enum, got {type(boolean_operator)}")
            query = f"{boolean_operator.value} {query}"

        self.queries.append(query)
        return self

    def _format_query_value(self, field: Field, value: Union[str, DateRange, Category]) -> str:
        """Format the query value based on field type.

        Args:
            field (SubCategory): The query field
            value (Union[str, DateRange, CATEGORY]): The value to format

        Returns:
            str: Formatted query value

        Raises:
            ValueError: If value type is invalid for the field
        """
        if field == Field.sumbitted_date:
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

    @staticmethod
    def _validate_category(value: Union[str, Category]) -> str:
        """
        Validate that the category is one of the predefined CATEGORY enum values.

        Args:
            value: The category value to validate.

        Returns:
            str: The validated category string.

        Raises:
            InvalidCategoryError: If the category is not in CATEGORY.
        """
        if isinstance(value, Category):
            return value.value
        elif isinstance(value, str) and value in {cat.value for cat in Category}:
            return value
        else:
            raise InvalidCategoryError(f"Invalid category: '{value}'. Use a valid CATEGORY enum value from CATEGORY.")

    def search_query(self) -> str:
        """
        Build the query string.

        Returns:
            str: A single query string for use with the arXiv API.
        """
        return " ".join(self.queries)

    def get_page(self, page: int = 1, search_query: str = None) -> FeedResults:
        search_query = search_query if search_query is not None else self.search_query()
        start = (page - 1) * self.max_results
        return Query.http_get(
            search_query=search_query, start=start, max_results=self.max_results, sortBy=self.sortBy, sortOrder=self.sortOrder, base_url=self.base_url
        )

    @staticmethod
    def from_feed_entry(entry: feedparser.FeedParserDict) -> Result:
        """
        Converts a feedparser entry for an arXiv search result feed into a
        Result object.
        """
        if not hasattr(entry, "id"):
            raise Result.MissingFieldError("id")
        # Title attribute may be absent for certain titles. Defaulting to "0" as
        # it's the only title observed to cause this bug.
        # https://github.com/lukasschwab/arxiv.py/issues/71
        # title = entry.title if hasattr(entry, "title") else "0"
        title = "0"
        if hasattr(entry, "title"):
            title = entry.title
        else:
            logger.warning("Result %s is missing title attribute; defaulting to '0'", entry.id)
        return Result(
            entry_id=entry.id,
            updated=Result._to_datetime(entry.updated_parsed),
            published=Result._to_datetime(entry.published_parsed),
            title=re.sub(r"\s+", " ", title),
            authors=[Result.Author._from_feed_author(a) for a in entry.authors],
            summary=entry.summary,
            comment=entry.get("arxiv_comment"),
            journal_ref=entry.get("arxiv_journal_ref"),
            doi=entry.get("arxiv_doi"),
            primary_category=entry.arxiv_primary_category.get("term"),
            categories=[tag.get("term") for tag in entry.tags],
            links=[Result.Link._from_feed_link(link) for link in entry.links],
            _raw=entry,
        )

    @staticmethod
    def http_get(
        base_url: str = "http://export.arxiv.org/api/query?",
        search_query: str = "",
        max_results: int = 5,
        sortBy: SortOrder = SortCriterion.SubmittedDate,
        sortOrder: SortOrder = SortOrder.Descending,
        start: int = 0,
    ) -> FeedResults:

        # Construct the parameters dictionary. Note that the search_query value contains quotes.
        params = {
            "search_query": search_query,
            "max_results": max_results,
            "sortBy": sortBy.value,
            "sortOrder": sortOrder.value,
            "start": start,
        }

        # Use urllib.parse.urlencode to encode the parameters properly.
        query_string = urllib.parse.urlencode(params)
        url = base_url + query_string

        logger.debug(f"Arxiv API Request URL:{url}")  # Debug: print the constructed URL

        # Perform a GET request using the properly constructed URL.
        response = urllib.request.urlopen(url).read()

        # Parse the response using feedparser.
        feed = feedparser.parse(response)
        total_results = int(getattr(feed.feed, "opensearch_totalresults", -1))
        start_index = int(getattr(feed.feed, "opensearch_startindex", -1))
        items_per_page = int(getattr(feed.feed, "opensearch_itemsperpage", -1))

        # Process and print each entry from the feed.
        results: List[Result] = []
        for entry in feed.entries:
            result = Query.from_feed_entry(entry)
            results.append(result)

        return FeedResults(results, total_results, start_index, items_per_page)