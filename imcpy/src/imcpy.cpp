#include <pybind11/pybind11.h>
#include <pybind11/stl_bind.h>
#include "generated/pbGenerated.hpp"

namespace py = pybind11;

// Forward declarations
void pbMessage(py::module &);
void pbPacket(py::module &);
void pbFactory(py::module &);
void pbConstants(py::module &);
void pbAlgorithms(py::module &);
void pbCoordinates(py::module &);

PYBIND11_MODULE(_imcpy, m) {
    m.doc() = "IMC bindings for python";

    // Bind classes
    pbMessage(m);
    pbPacket(m);
    pbFactory(m);
    pbAlgorithms(m);
    pbCoordinates(m);

    // Bind constants
    pbConstants(m);

    // Add classes
    pbGenerated(m);
}
