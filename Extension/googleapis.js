// uploadScript.js
document.getElementById('uploadButton').addEventListener('click', async function() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    if (!file) {
        alert('Please select a file.');
        return;
    }

    const apiKey = 'AIzaSyBop6_CQMPH8w4fJGgS3josH57YZaNnjWs';
    const displayName = 'TestScript';
    const baseUrl = 'https://generativelanguage.googleapis.com';

    try {
        const mimeType = file.type;
        const numBytes = file.size;
        const chunkSize = 8388608; // 8 MiB

        // Initial Resumable Session Setup
        const sessionResponse = await fetch(`${baseUrl}/upload/v1beta/files?key=${apiKey}`, {
            method: 'POST',
            headers: {
                'X-Goog-Upload-Protocol': 'resumable',
                'X-Goog-Upload-Command': 'start',
                'X-Goog-Upload-Header-Content-Length': numBytes,
                'X-Goog-Upload-Header-Content-Type': mimeType,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ file: { display_name: displayName } })
        });

        const sessionHeaders = await sessionResponse.headers.get('x-goog-upload-url');
        const uploadUrl = sessionHeaders;

        // Upload the chunks
        let offset = 0;
        while (offset < numBytes) {
            const chunk = file.slice(offset, offset + chunkSize);
            const chunkResponse = await fetch(uploadUrl, {
                method: 'POST',
                headers: {
                    'Content-Length': chunk.size,
                    'X-Goog-Upload-Offset': offset,
                    'X-Goog-Upload-Command': offset + chunk.size < numBytes ? 'upload' : 'upload, finalize'
                },
                body: chunk
            });

            if (!chunkResponse.ok) {
                throw new Error('Upload failed for a chunk.');
            }

            offset += chunk.size;
            console.log(`Uploaded ${offset} of ${numBytes}`);
        }

        console.log("Upload complete!");
    } catch (error) {
        console.error('Upload failed:', error);
    }
});
