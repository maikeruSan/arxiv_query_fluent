from arxiv_query_fluent import Query,Field,Category,Opt,DateRange
import logging
import pytest

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


@pytest.fixture
def query():
    return Query(max_results_per_paer=50)

def test_basic_query(query:Query):
    result = (
        query
        .add(Field.category, Category.CS_AI)
        .add(Field.author,"Stas Tiomkin",Opt.And)
        .add(
            Field.sumbitted_date,
            DateRange("20220101","20241231"),
            Opt.And
        )
        .search_query()
    )
    logger.info(result)

    assert  result == 'cat:"cs.AI" AND au:"Stas Tiomkin" AND submittedDate:[202201010000 TO 202412312359]'


def test_grouop_query():
    group_1 =  Query().add(Field.author,"Stas Tiomkin").add(Field.author,"Daniel Polani",Opt.And)
    group_2 =  Query().add(Field.title,"Dynamic",Opt.Or).add(Field.sumbitted_date,DateRange("20240101","20241231"),Opt.Or)

    query = (
        Query()
        .add_group(group_1)
        .add_group(group_2,Opt.And_Not)
    )

    assert query.search_query()=='(au:"Stas Tiomkin" AND au:"Daniel Polani") ANDNOT (ti:"Dynamic" OR submittedDate:[202401010000 TO 202412312359])'
    results = query.get_page()
    assert results.totalResults == 1
    paper = results.entrys[0]
    assert paper.download_pdf(filename=f"{paper.get_short_id()}.pdf") is not None 