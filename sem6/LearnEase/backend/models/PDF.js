const mongoose = require("mongoose");

const pdfSchema = new mongoose.Schema({
  filename: String,
  fileUrl: String, 
  uploadedAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model("PDF", pdfSchema);
