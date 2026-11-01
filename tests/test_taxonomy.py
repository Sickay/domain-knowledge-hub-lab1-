import pytest
from rdflib import Graph, SKOS, RDF


@pytest.fixture
def skos_graph():
    g = Graph()
    g.parse("models/taxonomy.ttl", format="turtle")
    return g


def test_skos_validity(skos_graph):
    assert len(skos_graph) > 0


def test_pref_labels_exist(skos_graph):
    query = """
        SELECT ?concept ?label WHERE {
            ?concept rdf:type skos:Concept .
            ?concept skos:prefLabel ?label .
        }
    """
    results = list(skos_graph.query(query))
    assert len(results) >= 4


def test_no_orphan_concepts(skos_graph):
    query = """
        SELECT ?concept WHERE {
            ?concept rdf:type skos:Concept .
            FILTER NOT EXISTS { ?concept skos:broader ?parent . }
            FILTER NOT EXISTS { ?concept skos:prefLabel "Промислова автоматизація"@uk . }
        }
    """
    results = list(skos_graph.query(query))
    assert len(results) == 0


def test_definitions_exist(skos_graph):
    query = """
        SELECT ?concept WHERE {
            ?concept rdf:type skos:Concept .
            FILTER NOT EXISTS { ?concept skos:definition ?def . }
        }
    """
    results = list(skos_graph.query(query))
    assert len(results) == 0


def test_external_matches(skos_graph):
    query = """
        SELECT ?concept ?match WHERE {
            ?concept skos:exactMatch ?match .
        }
    """
    results = list(skos_graph.query(query))
    assert len(results) >= 2


def test_concept_scheme_exists(skos_graph):
    schemes = list(skos_graph.subjects(RDF.type, SKOS.ConceptScheme))
    assert len(schemes) == 1
