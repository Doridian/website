package main

import (
	"crypto/rand"
	"embed"
	"fmt"
	"io"
	"io/fs"
	"log"
	"math/big"
	"net/http"
	"path"
)

//go:embed epaper/*
var epaperImages embed.FS
var epaperFiles []fs.DirEntry

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

func ePaperImageHandler(w http.ResponseWriter, r *http.Request) error {
	token := r.URL.Query().Get("token")

	var fileIndexSize = int64(len(epaperFiles))
	canEvade := false
	if token != "" {
		fileIndexSize--
		canEvade = true
	}

	fileIndexBig, err := rand.Int(rand.Reader, big.NewInt(fileIndexSize))
	if err != nil {
		log.Printf("Error getting random ePaper file index: %v", err)
		return err
	}

	fileIndex := fileIndexBig.Int64()
	if canEvade && epaperFiles[fileIndex].Name() == token {
		fileIndex++
	}

	fileObject := epaperFiles[fileIndex]
	fileName := fileObject.Name()

	fileInfo, err := fileObject.Info()
	if err != nil {
		log.Printf("Error getting ePaper file info: %v", err)
		return err
	}
	file, err := epaperImages.Open(path.Join("epaper", fileName))
	if err != nil {
		log.Printf("Error getting ePaper file handle: %v", err)
		return err
	}

	w.Header().Add("Content-Type", "application/octet-stream")
	w.Header().Add("Content-Disposition", fmt.Sprintf("attachment; filename=%s", fileName))
	w.Header().Add("Content-Length", fmt.Sprintf("%d", fileInfo.Size()))
	w.Header().Add("Token", fileName)
	w.WriteHeader(http.StatusOK)
	_, err = io.Copy(w, file)
	if err != nil {
		log.Printf("Error copying ePaper file data: %v", err)
		return err
	}

	return nil
}

func main() {
	var err error
	epaperFiles, err = epaperImages.ReadDir("epaper")
	if err != nil {
		panic(err)
	}

	http.Handle("/api/e-paper-image", &ErroringHTTPHandler{subHandler: ePaperImageHandler})

	log.Fatal(http.ListenAndServe("127.0.0.1:8080", nil))
}
