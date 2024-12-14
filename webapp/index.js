require("dotenv").config();

const express = require("express");
const multer = require("multer");
const path = require("path");
const cors = require("cors");
const {
  listMedia,
  uploadMedia,
  updateMediaMetadata,
  deleteMedia,
} = require("./src/azureUtils");

const app = express();
const upload = multer(); // For handling multipart form data (file uploads)
const PORT = 3000;

// Middleware to parse JSON bodies
app.use(express.json());

// Enable CORS for all routes
app.use(cors());

// Serve the React static files
const FRONTEND_BUILD_PATH = path.join(__dirname, "./client/build");
app.use(express.static(FRONTEND_BUILD_PATH));

// GET /media - List all media files
app.get("/media", async (req, res) => {
  try {
    const mediaList = await listMedia();
    res.json(mediaList);
  } catch (error) {
    console.error("Error listing media:", error.message);
    res.status(500).send("Failed to list media files.");
  }
});

// POST /media - Upload a new media file
app.post("/media", upload.single("file"), async (req, res) => {
  try {
    if (!req.file) return res.status(400).send("No file uploaded.");

    const filePath = req.body.path; // Full path (e.g., splash/image.jpg)
    console.log(filePath);
    await uploadMedia(req.file, filePath);
    res.status(201).send("Media uploaded successfully.");
  } catch (error) {
    console.error("Error uploading media:", error.message);
    res.status(500).send("Failed to upload media file.");
  }
});

app.put("/media", async (req, res) => {
  try {
    const blobPath = req.body.id; // Blob path includes folder (e.g., 'splash/jess_chris1.jpg')
    const metadata = req.body.metadata;

    if (!metadata || typeof metadata !== "object") {
      return res.status(400).send("Invalid metadata format.");
    }

    await updateMediaMetadata(blobPath, metadata);
    res.send(`Metadata updated for ${blobPath}`);
  } catch (error) {
    console.error("Error updating metadata:", error.message);
    res.status(500).send("Failed to update media metadata.");
  }
});

// DELETE /media - delete a blob
app.delete("/media", async (req, res) => {
  try {
    const { id } = req.body; // Full blob path (e.g., 'images/photo1.jpg')
    if (!id) {
      return res
        .status(400)
        .json({ message: "Blob 'id' is required in the request body." });
    }

    // Call azureUtils deleteMedia method
    await deleteMedia(id);
    res.status(200).json({ message: `Blob '${id}' deleted successfully.` });
  } catch (error) {
    console.error("Error deleting media:", error.message);
    res
      .status(500)
      .json({ message: error.message || "Failed to delete media." });
  }
});

// ROOT / - Serve web app (to be added later)
app.get("/", (req, res) => {
  res.sendFile(path.join(FRONTEND_BUILD_PATH, "index.html"));
});

// Start the server
app.listen(PORT, "0.0.0.0", () => {
  console.log(`Server running at http://<YOUR_PI_IP>:${PORT}`);
});
