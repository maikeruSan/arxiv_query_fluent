import pytest
import urllib.request
from arxiv_query_fluent import (
    Query,
    Field,
    Category,
    Opt,
    DateRange,
    InvalidDateFormatError,
    InvalidCategoryError,
    PrependOperatorError,
)
from arxiv import SortCriterion, SortOrder
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


@pytest.fixture
def query() -> Query:
    return Query(max_entries_per_pager=50)


class TestQueryBasic:
    """Tests for basic Query functionality."""

    def test_basic_query(self, query: Query):
        result = (
            query.add(Field.category, Category.CS_AI)
            .add(Field.author, "Stas Tiomkin", Opt.And)
            .add(Field.submitted_date, DateRange("20220101", "20241231"), Opt.And)
            .search_query()
        )
        logger.info(result)
        expected = 'cat:"cs.AI" AND au:"Stas Tiomkin" AND submittedDate:[202201010000 TO 202412312359]'
        assert result == expected

    def test_group_query(self):
        group_1 = Query().add(Field.author, "Stas Tiomkin").add(Field.author, "Daniel Polani", Opt.And)
        group_2 = Query().add(Field.title, "Dynamic", Opt.Or).add(Field.submitted_date, DateRange("20240101", "20241231"), Opt.Or)
        query_instance = Query().add_group(group_1).add_group(group_2, Opt.And_Not)
        expected = '(au:"Stas Tiomkin" AND au:"Daniel Polani") ANDNOT (ti:"Dynamic" OR submittedDate:[202401010000 TO 202412312359])'
        assert query_instance.search_query() == expected

        results = query_instance.get()
        assert results.total_entries_of_query == 1
        paper = results.entrys[0]
        # Assuming download_pdf returns a non-None value if successful
        assert paper.download_pdf(filename=f"{paper.get_short_id()}.pdf") is not None


class TestDateRange:
    """Tests for DateRange functionality."""

    def test_valid_date_8_digits(self):
        dr = DateRange("20240101", "20240131")
        assert str(dr) == "[202401010000 TO 202401312359]"

    def test_valid_date_12_digits(self):
        dr = DateRange("202401010101", "202401312359")
        assert str(dr) == "[202401010101 TO 202401312359]"

    def test_invalid_date_format_length(self):
        with pytest.raises(InvalidDateFormatError):
            DateRange("202401", "20240131")

    def test_invalid_date_non_existent(self):
        with pytest.raises(InvalidDateFormatError):
            DateRange("20240230", "20240301")

    def test_invalid_date_characters(self):
        with pytest.raises(InvalidDateFormatError):
            DateRange("2024abcd", "20240131")

    def test_invalid_date_range_start_after_end(self):
        with pytest.raises(InvalidDateFormatError):
            DateRange("20240131", "20240101")


class TestQueryValidation:
    """Tests for Query input validation."""

    def test_add_invalid_field(self):
        query_instance = Query()
        with pytest.raises(ValueError):
            query_instance.add("invalid_field", "Some Value")

    def test_add_invalid_category_value(self):
        query_instance = Query()
        with pytest.raises(InvalidCategoryError):
            query_instance.add(Field.category, "invalid_category_value")

    def test_prepend_boolean_operator_missing(self):
        query_instance = Query()
        query_instance.add(Field.author, "John Doe")
        with pytest.raises(PrependOperatorError):
            query_instance.add(Field.title, "Quantum Computing")


class TestUrlAndFormatting:
    """Tests for URL building and query value formatting."""

    def test_build_arxiv_url(self):
        base_url = "http://export.arxiv.org/api/query?"
        search_query = 'au:"John Doe"'
        max_results = 10
        sortBy = SortCriterion.SubmittedDate
        sortOrder = SortOrder.Descending
        start = 20
        url = Query._build_arxiv_url(base_url, search_query, max_results, sortBy, sortOrder, start)
        assert "search_query=au%3A%22John+Doe%22" in url
        assert "max_results=10" in url
        assert "sortBy=submittedDate" in url
        assert "sortOrder=descending" in url
        assert "start=20" in url

    def test_format_query_value_with_date_range(self):
        query_instance = Query()
        dr = DateRange("20240101", "20240131")
        formatted_value = query_instance._format_query_value(Field.submitted_date, dr)
        assert formatted_value == str(dr)

    def test_format_query_value_with_string(self):
        query_instance = Query()
        value = "Alice Smith"
        formatted_value = query_instance._format_query_value(Field.author, value)
        assert formatted_value == f'"{value}"'


class TestPagination:
    """Tests for pagination functionality."""

    @pytest.mark.xfail(reason="get() does not currently enforce page >= 1")
    def test_get_invalid_page(self):
        query_instance = Query()
        with pytest.raises(ValueError):
            query_instance.get(page=0)
