import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [docType, setDocType] = useState("pan");
  const [file, setFile] = useState(null);
  const [number, setNumber] = useState("");
  const [result, setResult] = useState(null);

  const baseURL = "http://127.0.0.1:8000/api";

  const getEndpoints = () => {
    if (docType === "pan") {
      return {
        upload: `${baseURL}/upload-pan/`,
        verify: `${baseURL}/verify-pan/${number}/`,
      };
    }
    if (docType === "gst") {
      return {
        upload: `${baseURL}/upload-gst/`,
        verify: `${baseURL}/verify-gst/${number}/`,
      };
    }
    if (docType === "cin") {
      return {
        upload: `${baseURL}/upload-cin/`,
        verify: `${baseURL}/verify-cin/${number}/`,
      };
    }
  };

  const handleUpload = async () => {
    if (!file) return alert("Select a file first");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const { upload } = getEndpoints();
      const res = await axios.post(upload, formData);
      setResult(res.data);
    } catch (err) {
      alert("Upload failed");
    }
  };

  const handleVerify = async () => {
    if (!number) return alert("Enter number");

    try {
      const { verify } = getEndpoints();
      const res = await axios.get(verify);
      setResult(res.data);
    } catch (err) {
      alert("Verification failed");
    }
  };

  return (
    <div className="container">
      <h1>Document Verification</h1>

      {/* Tabs */}
      <div className="tabs">
        <button onClick={() => setDocType("pan")}>PAN</button>
        <button onClick={() => setDocType("gst")}>GST</button>
        <button onClick={() => setDocType("cin")}>CIN</button>
      </div>

      {/* Upload */}
      <div className="section">
        <h2>Upload {docType.toUpperCase()}</h2>
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        <button onClick={handleUpload}>Upload</button>
      </div>

      {/* Verify */}
      <div className="section">
        <h2>Verify {docType.toUpperCase()}</h2>
        <input
          type="text"
          placeholder={`Enter ${docType.toUpperCase()} number`}
          value={number}
          onChange={(e) => setNumber(e.target.value)}
        />
        <button onClick={handleVerify}>Verify</button>
      </div>

      {/* Result */}
      {result && (
        <div className="result">
          <h3>Status: {result.status}</h3>
          {result.data &&
            Object.entries(result.data).map(([key, value]) => (
              <p key={key}>
                <strong>{key}:</strong> {value}
              </p>
            ))}
        </div>
      )}
    </div>
  );
}

export default App;
