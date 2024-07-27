package main

import (
	"log"
	"net/http"
)

type HTTPErroringHandlerFunc = func(w http.ResponseWriter, r *http.Request) error

type ErroringHTTPHandler struct {
	subHandler HTTPErroringHandlerFunc
}

func (h *ErroringHTTPHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	err := h.subHandler(w, r)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte("Internal Server Error"))
	}
}

func testHandler(w http.ResponseWriter, r *http.Request) error {
	w.WriteHeader(200)
	w.Write([]byte("Hello, World!"))
	return nil
}

func main() {
	http.Handle("/api/test", &ErroringHTTPHandler{subHandler: testHandler})

	log.Print("Server ready, starting listener!")
	log.Fatal(http.ListenAndServe("127.0.0.1:8080", nil))
}
