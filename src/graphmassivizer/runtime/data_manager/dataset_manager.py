from pathlib import Path
from graphmassivizer.runtime.data_manager.data_manager import DataManager
from rdflib import Graph, URIRef
from rdflib.query import Result as QueryResult
from rdflib.plugins.sparql.sparql import Query
from rdflib.util import SUFFIX_FORMAT_MAP


class DatasetManagerDisk(DataManager):
    def __init__(self, path_to_input_file: Path) -> None:
        if not path_to_input_file.is_file:
            raise Exception("The provided dataset file does not exist")
        if path_to_input_file.suffixes != [".nt"]:
            file_extension_string = "".join(path_to_input_file.suffixes)
            raise Exception(
                f"The dataset file type ({file_extension_string}) does not match the expected type (.nt)"
            )

        self._graph_location = path_to_input_file
        self._in_memory_graph = Graph()

    @property
    def graph_location(self) -> Path:
        return self._graph_location

    @property
    def graph(self) -> Graph:
        return self._in_memory_graph

    @graph_location.setter
    def graph_location(self, path_to_input_file: Path) -> None:
        self._graph_location = path_to_input_file

    def create(self) -> None:
        pass  # TODO implement later if we want to create an output disk file

    def read(self) -> QueryResult:
        self._in_memory_graph.parse(self._graph_location)
        return self._in_memory_graph.query(query)

    def update(self) -> None:
        pass  # TODO implement later if we want to mutate the input/output disk file

    def delete(self) -> None:
        pass  # TODO implement later if we want to remove the input disk file


if __name__ == "__main__":
    import os

    rdf_file = Path(os.path.dirname(os.path.abspath(__file__)) + "/test_rdf.nt")
    data_manager = DatasetManagerDisk(rdf_file)

    query = """
            SELECT ?s ?p ?o
            WHERE
            {
            ?s ?p ?o .
            }
            """

    results = data_manager.read()
    for row in results:
        print(f"Subject: {row.s}, Predicate: {row.p}, Object: {row.o}")

    # # REMOTE QUERY EXAMPLES:

    # # Query dbpedia
    # g = Graph()
    # qres = g.query(
    #     """
    #     SELECT ?s
    #     WHERE {
    #     SERVICE <https://dbpedia.org/sparql> {
    #         ?s a ?o .
    #     }
    #     }
    #     LIMIT 3
    #     """
    # )

    # # Query wikidata
    # for row in qres:
    #     print(row.s)

    # wd = URIRef("http://www.wikidata.org/entity/")
    # wdt = URIRef("http://www.wikidata.org/prop/direct/")

    # qres = g.query(
    #     """
    #     SELECT ?item
    #     WHERE {
    #     SERVICE <https://query.wikidata.org/sparql> {
    #         ?item wdt:P31 wd:Q146.
    #     }
    #     }
    #     LIMIT 3
    #     """,
    #     initNs={"wd": wd, "wdt": wdt}
    # )

    # for row in qres:
    #     print(row.item)
