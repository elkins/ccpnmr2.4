#include <Python.h>
#include "spectral_processing.h"

/* Python wrapper for exponential_apodization */
static PyObject* py_exponential_apodization(PyObject* self, PyObject* args) {
    PyObject *real_obj, *imag_obj;
    double lb;
    
    if (!PyArg_ParseTuple(args, "OOd", &real_obj, &imag_obj, &lb)) {
        return NULL;
    }
    
    // Convert Python lists to C arrays
    Py_ssize_t size = PyList_Size(real_obj);
    double *fid_real = (double*)malloc(size * sizeof(double));
    double *fid_imag = (double*)malloc(size * sizeof(double));
    
    for (Py_ssize_t i = 0; i < size; i++) {
        fid_real[i] = PyFloat_AsDouble(PyList_GetItem(real_obj, i));
        fid_imag[i] = PyFloat_AsDouble(PyList_GetItem(imag_obj, i));
    }
    
    // Call the C function
    exponential_apodization(fid_real, fid_imag, (int)size, lb);
    
    // Convert back to Python
    PyObject *result_real = PyList_New(size);
    PyObject *result_imag = PyList_New(size);
    
    for (Py_ssize_t i = 0; i < size; i++) {
        PyList_SetItem(result_real, i, PyFloat_FromDouble(fid_real[i]));
        PyList_SetItem(result_imag, i, PyFloat_FromDouble(fid_imag[i]));
    }
    
    free(fid_real);
    free(fid_imag);
    
    return Py_BuildValue("(OO)", result_real, result_imag);
}

/* Module definition */
static PyMethodDef CExtensionMethods[] = {
    {"exponential_apodization", py_exponential_apodization, METH_VARARGS, 
     "Apply exponential apodization to FID data"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef cextensionmodule = {
    PyModuleDef_HEAD_INIT,
    "cextension",
    "C extension for NMR spectral processing",
    -1,
    CExtensionMethods
};

PyMODINIT_FUNC PyInit_cextension(void) {
    return PyModule_Create(&cextensionmodule);
}
