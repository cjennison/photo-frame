import React, { useState, useEffect } from "react";
import { updateMedia, deleteMedia } from "../api";

function MediaItem({ media, onDelete, onSave }) {
  const [contents, setContents] = useState(media.metadata.contents || "");
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const timeout = setTimeout(() => {
      setSuccess(false);
    }, 3000);

    return () => clearTimeout(timeout);
  }, [success]);

  // Handle Save button click
  const handleSave = async () => {
    try {
      await updateMedia(media.id, { contents });
      setSuccess(true);
      onSave(true);
    } catch (error) {
      console.error("Error saving metadata:", error);
      alert("Failed to update metadata.");
    }
  };

  // Handle Delete button click
  const handleDelete = async () => {
    if (window.confirm("Are you sure you want to delete this media?")) {
      try {
        await deleteMedia(media.id);
        onDelete();
      } catch (error) {
        console.error("Error deleting media:", error);
        alert("Failed to delete media.");
      }
    }
  };

  // Determine whether the media is a video
  const isVideo = media.id.endsWith(".mp4");

  return (
    <div style={styles.card} className="card">
      <div style={styles.mediaContainer}>
        {isVideo ? (
          <video controls style={styles.media}>
            <source src={media.url} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        ) : (
          <img
            src={media.url}
            alt="thumbnail"
            style={styles.media}
            loading="lazy"
          />
        )}
      </div>
      <div style={styles.content} className="card-content">
        <div style={styles.title} className="title">
          {media.id}
        </div>
        <form>
          <label>
            {success ? "Updated!" : "Contents:"}
            <input
              type="text"
              value={contents}
              onChange={(e) => setContents(e.target.value)}
              style={styles.input}
            />
          </label>
        </form>
        <div style={styles.actions}>
          <button
            onClick={handleDelete}
            style={{
              ...styles.button,
              background: "transparent",
              color: "Red",
            }}
          >
            Delete
          </button>
          <button
            onClick={handleSave}
            style={{
              ...styles.button,
              background: "#3498db",
            }}
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}

const styles = {
  card: {
    display: "flex",
    flexDirection: "column",
    border: "1px solid #ddd",
    borderRadius: "8px",
    boxShadow: "0 2px 4px rgba(0, 0, 0, 0.2)",
    margin: "10px",
    width: "200px",
    overflow: "hidden",
  },
  title: {
    padding: "2px 10px 5px",
    borderBottom: "1px solid #ddd",
    fontSize: "1em",
    fontWeight: "bold",
  },
  thumbnail: {
    width: "100%",
    height: "auto",
  },
  content: {
    padding: "10px",
    flex: 1,
  },
  input: {
    width: "100%",
    padding: "5px",
    marginTop: "5px",
    boxSizing: "border-box",
  },
  actions: {
    marginTop: "10px",
    display: "flex",
    justifyContent: "space-between",
  },
  button: {
    padding: "5px 10px",
    backgroundColor: "#3498db",
    color: "#fff",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
  },
  mediaContainer: {
    width: "100%",
    height: "60%", // Media container takes 60% of the card's height
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#f8f8f8", // Light background for media container
  },
  media: {
    width: "100%",
    height: "100%",
    objectFit: "cover", // Scale the content proportionally
  },
};

export default MediaItem;
