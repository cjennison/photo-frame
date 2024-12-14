import React, { useEffect, useState } from "react";
import "./App.css";

import MediaItem from "./components/MediaItem";
import { fetchMedia, uploadMedia } from "./api";

function App() {
  const [splashMedia, setSplashMedia] = useState([]);
  const [mainMedia, setMainMedia] = useState([]);
  const [splashFile, setSplashFile] = useState(null);
  const [mainFile, setMainFile] = useState(null);
  const [searchTerms, setSearchTerms] = useState([]);

  // Fetch media list and split into splash and main media
  const fetchMediaList = async () => {
    try {
      const mediaList = await fetchMedia();

      // Filter media into splash and main media
      const splash = mediaList.filter((item) => item.folder === "splash");
      const main = mediaList.filter((item) => item.folder !== "splash");

      setSplashMedia(splash);
      setMainMedia(main);

      // Extract and deduplicate searchable terms
      const terms = new Set();
      mediaList.forEach((item) => {
        if (item.metadata.contents) {
          item.metadata.contents
            .split(",")
            .forEach((term) => terms.add(term.trim()));
        }
      });
      setSearchTerms(Array.from(terms));
    } catch (error) {
      console.error("Error fetching media:", error);
    }
  };

  useEffect(() => {
    fetchMediaList();
  }, []);

  const handleDelete = () => fetchMediaList();
  const handleSave = () => fetchMediaList();

  // Handle upload for splash and main
  const handleUpload = async (file, isSplash) => {
    if (!file) return alert("No file selected!");

    // Determine folder and validate file type
    const fileName = file.name.toLowerCase();
    let folder = "";

    if (file.type.startsWith("image/")) {
      folder = isSplash ? "splash/" : "photos/";
    } else if (file.type === "video/mp4") {
      folder = "videos/";
    } else {
      alert("Only images and MP4 videos are allowed!");
      return;
    }

    try {
      const fullPath = `${folder}${fileName}`;
      await uploadMedia(file, fullPath);
      alert("File uploaded successfully!");
      fetchMediaList();
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("Failed to upload file.");
    }
  };

  return (
    <div className="App">
      <h1>ePi-Frame Media Manager</h1>
      {/* Search Terms Section */}
      <div className="search-terms-section">
        <h2>Searchable Terms</h2>
        <p>
          These are the unique set of keys in your content that show up on the
          device. It is recommended not to exceed 8 different terms.
        </p>
        <div className="pill-container">
          {searchTerms.length > 0 ? (
            searchTerms.map((term, index) => (
              <span key={index} className="pill">
                {term}
              </span>
            ))
          ) : (
            <p>No searchable terms available.</p>
          )}
        </div>
      </div>
      <hr />
      {/* Splash Media Section */}
      <h2>Splash Images</h2>
      {/* Splash Upload */}
      <p>
        Splash images are shown only once when the device turns on at random.
      </p>
      <div className="upload-section">
        <h2>Upload Splash Image</h2>
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setSplashFile(e.target.files[0])}
        />
        <button onClick={() => handleUpload(splashFile, true)}>Upload</button>
      </div>
      <div className="card-container">
        {splashMedia.map((item) => (
          <MediaItem
            key={item.id}
            media={item}
            onDelete={handleDelete}
            onSave={handleSave}
          />
        ))}
      </div>
      <hr /> {/* Horizontal ruler */}
      {/* Main Media Section */}
      <h2>Main Media</h2>
      <p>
        The main library order is random when the device starts, but all media
        is displayed once before looping. <br />
        <i>After uploading, restart the device to update it with new photos.</i>
      </p>
      <p>
        <b>Contents:</b> <br />
        The contents input field is used to add filtering terms for use in the
        device. <br />
        Separate each term with a comma.
      </p>
      {/* Main Upload */}
      <div className="upload-section">
        <h2>Upload Main Media</h2>
        <input
          type="file"
          accept="image/*,video/mp4"
          onChange={(e) => setMainFile(e.target.files[0])}
        />
        <button onClick={() => handleUpload(mainFile, false)}>Upload</button>
      </div>
      <div className="card-container">
        {mainMedia.map((item) => (
          <MediaItem
            key={item.id}
            media={item}
            onDelete={handleDelete}
            onSave={handleSave}
          />
        ))}
      </div>
    </div>
  );
}

export default App;
