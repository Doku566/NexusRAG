#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "nexus/index_core.hpp"

namespace py = pybind11;

PYBIND11_MODULE(nexus_core, m) {
    m.doc() = "NexusRAG Core Indexer";

    py::class_<nexus::SearchResult>(m, "SearchResult")
        .def_readonly("id", &nexus::SearchResult::id)
        .def_readonly("distance", &nexus::SearchResult::distance);

    py::class_<nexus::VectorIndex>(m, "VectorIndex")
        .def(py::init<int>(), py::arg("dimension"))
        .def("add_item", &nexus::VectorIndex::add_item, 
             py::arg("id"), py::arg("vector"),
             "Add a vector to the index (Thread-safe)")
        .def("search", &nexus::VectorIndex::search, 
             py::arg("query"), py::arg("k"),
             py::call_guard<py::gil_scoped_release>(), // CRITICAL: Release GIL!
             "Search for nearest neighbors. Releases GIL to allow concurrency.");
}
