package main

import (
	"embed"
	"io"
	"log"
	"math/rand"
	"net/http"
	"path"
)

//go:embed epaper/*
var epaperImages embed.FS

func main() {
	epaperFiles, err := epaperImages.ReadDir("epaper")
	if err != nil {
		panic(err)
	}

	http.HandleFunc("/api/e-paper-image", func(w http.ResponseWriter, r *http.Request) {
		fileIndex := rand.Intn(len(epaperFiles))
		fileName := epaperFiles[fileIndex].Name()
		file, fileErr := epaperImages.Open(path.Join("epaper", fileName))
		if fileErr != nil {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte("Internal Server Error"))
			return
		}
		w.Header().Add("Content-Type", "application/octet-stream")
		w.Header().Add("File-Name", fileName)
		w.WriteHeader(http.StatusOK)
		io.Copy(w, file)
	})

	log.Fatal(http.ListenAndServe("127.0.0.1:8080", nil))
}
