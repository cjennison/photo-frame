const {
  BlobServiceClient,
  generateBlobSASQueryParameters,
  BlobSASPermissions,
  StorageSharedKeyCredential,
} = require("@azure/storage-blob");

const AZURE_CONNECTION_STRING = process.env.AZURE_CONNECTION_STRING;
const CONTAINER_NAME = process.env.AZURE_CONTAINER_NAME;
const CONTAINER_KEY = process.env.AZURE_CONTAINER_KEY;
const ACCOUNT_NAME = process.env.AZURE_CONTAINER_ACCOUNT_NAME;

const storageSharedKeyCredential = new StorageSharedKeyCredential(
  ACCOUNT_NAME,
  CONTAINER_KEY
);
const blobServiceClient = BlobServiceClient.fromConnectionString(
  AZURE_CONNECTION_STRING
);
const containerClient = blobServiceClient.getContainerClient(CONTAINER_NAME);

function generateSasUrl(blobName) {
  const expiryDate = new Date();
  expiryDate.setHours(expiryDate.getHours() + 1); // SAS valid for 1 hour

  const sasToken = generateBlobSASQueryParameters(
    {
      containerName: CONTAINER_NAME,
      blobName: blobName,
      permissions: BlobSASPermissions.parse("r"), // Read permissions
      expiresOn: expiryDate,
    },
    storageSharedKeyCredential
  ).toString();

  return `https://${ACCOUNT_NAME}.blob.core.windows.net/${CONTAINER_NAME}/${blobName}?${sasToken}`;
}

// List all blobs in the container
async function listMedia() {
  let blobs = [];
  for await (const blob of containerClient.listBlobsFlat({
    includeMetadata: true,
  })) {
    blobs.push({
      id: blob.name,
      folder: blob.name.split("/")[0],
      url: generateSasUrl(blob.name),
      metadata: blob.metadata || {},
    });
  }
  return blobs;
}

// Upload a new blob to the specified path
async function uploadMedia(file, blobPath) {
  const blockBlobClient = containerClient.getBlockBlobClient(blobPath); // Path includes folder name
  await blockBlobClient.uploadData(file.buffer, { overwrite: true });
}

// Update metadata of a specific blob (supports folder paths)
async function updateMediaMetadata(blobPath, metadata) {
  const blobClient = containerClient.getBlobClient(blobPath);
  await blobClient.setMetadata(metadata);
}

// Delete a blob
async function deleteMedia(blobPath) {
  const blobClient = containerClient.getBlobClient(blobPath);
  const exists = await blobClient.exists();
  if (!exists) {
    throw new Error(`Blob '${blobPath}' does not exist.`);
  }
  await blobClient.delete();
}

module.exports = { listMedia, uploadMedia, updateMediaMetadata, deleteMedia };
