const express = require("express");
const multer = require("multer");
const path = require("path");
const axios = require("axios"); // To call the FastAPI service
const fs = require("fs");
const FormData = require("form-data"); // For sending files
const PDF = require("../models/PDF");

const router = express.Router();

// Define local storage location
const storage = multer.diskStorage({
  destination: "./uploads", // Store files in "uploads" folder
  filename: (req, file, cb) => {
    cb(null, Date.now() + path.extname(file.originalname)); // Unique filename
  },
});

const upload = multer({ storage });

// Upload API
router.post("/", upload.single("file"), async (req, res) => {
  try {
    if (!req.file) return res.status(400).json({ error: "No file uploaded" });

    // Get file path
    const filePath = req.file.path;

    // Step 1: Send the PDF to FastAPI for summarization
    const formData = new FormData();
    formData.append("file", fs.createReadStream(filePath));

    const summaryResponse = await axios.post(
      "http://localhost:8000/upload_pdf/", // FastAPI endpoint
      formData,
      { headers: { ...formData.getHeaders() } }
    );

    if (!summaryResponse.data || summaryResponse.data.error) {
      return res.status(500).json({ error: "Failed to generate summary" });
    }

    const summary = summaryResponse.data.summary;

    // Step 2: Save metadata & summary to MongoDB
    const newPDF = new PDF({
      filename: req.file.originalname,
      filePath: filePath, // Store local file path
      summary: summary, // Store generated summary
    });

    await newPDF.save();

    res.json({ message: "File uploaded & summarized successfully", pdf: newPDF });
  } catch (error) {
    console.error("Error:", error.message);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
