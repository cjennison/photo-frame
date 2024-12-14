const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "/media";

// Fetch all media files (GET)
export const fetchMedia = async () => {
  console.log("API_BASE_URL:", API_BASE_URL);
  try {
    const response = await fetch(API_BASE_URL);
    console.log("Response:", response);
    if (!response.ok) throw new Error("Failed to fetch media.");
    return await response.json();
  } catch (error) {
    console.error("Error fetching media:", error);
    throw error;
  }
};

// Upload a new media file (POST)
export const uploadMedia = async (file, path) => {
  try {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("path", path);

    const response = await fetch(API_BASE_URL, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error("Failed to upload media.");
    return await response.text(); // Success message
  } catch (error) {
    console.error("Error uploading media:", error);
    throw error;
  }
};

// Update media metadata (PUT)
export const updateMedia = async (id, metadata) => {
  try {
    const response = await fetch(`${API_BASE_URL}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        id,
        metadata,
      }),
    });

    if (!response.ok) throw new Error("Failed to update media metadata.");
    return await response.text(); // Success message
  } catch (error) {
    console.error("Error updating media:", error);
    throw error;
  }
};

// Delete a media file (DELETE)
export const deleteMedia = async (id) => {
  try {
    const response = await fetch(`${API_BASE_URL}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        id,
      }),
    });

    if (!response.ok) throw new Error("Failed to delete media.");
    return await response.text(); // Success message
  } catch (error) {
    console.error("Error deleting media:", error);
    throw error;
  }
};
