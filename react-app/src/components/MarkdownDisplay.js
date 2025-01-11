import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';



function isLikelyMarkdown(text) {
  const patterns = [
    /^#{1,6}\s/m,                     // Headers (allow multiple #)
    /\*\*(.*?)\*\*/,                  // Bold
    /\*(.*?)\*/,                      // Italic
    /\[.*?\]\(.*?\)/,                 // Links
    /^\s*[-*+]\s/m,                   // Unordered lists (level 1)
    /^\s{2,}[-*+]\s/m,               // Nested unordered lists
    /^\s*\d+\.\s/m,                   // Ordered lists
    /`{1,3}[^`\n]+`{1,3}/,           // Code blocks/inline
    /^\s*>/m,                         // Blockquotes
    /^([-*_]){3,}$/m,                // Horizontal rules
    /!\[.*?\]\(.*?\)/                // Images
  ];
  
  // Test each line separately
  const lines = text.split('\n');
  return lines.some(line => 
    patterns.some(pattern => pattern.test(line))
  );
}
const MarkdownDisplay = ({ content, className, style }) => {
  const [copySuccess, setCopySuccess] = useState('');
  const isMarkdown = isLikelyMarkdown(content);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopySuccess('Copied!');
      setTimeout(() => setCopySuccess(''), 2000);
    } catch (err) {
      setCopySuccess('Failed to copy');
      console.error('Failed to copy: ', err);
    }
  };

  return (
    <div className={`content-display ${className || 'pre-format'}`} style={style}>
      {isMarkdown ? (
        <div className='markdown-content'>
          <ReactMarkdown>
            {content}
          </ReactMarkdown>
        </div>
      ) : (
        <pre className='pre-format' style={{ maxWidth: "800px", backgroundColor: "white"}}>
          {content}
        </pre>
      )}

      <div className="copy-button-container">
        <button onClick={handleCopy} className="copy-button">
          Copy to Clipboard
        </button>
        {copySuccess && <span className="copy-status">{copySuccess}</span>}
      </div>
    </div>
  );
};

export default MarkdownDisplay;