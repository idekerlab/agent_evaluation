import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';

function isLikelyMarkdown(text) {
  const patterns = [
    /^#\s/, /\*\*(.*?)\*\*/, /\*(.*?)\*/, /\[.*?\]\(.*?\)/, /^\s*[-*+]\s/,
    /^\s*\d+\.\s/, /`{1,3}[^`\n]+`{1,3}/, /^\s*>/, /^([-*_]){3,}$/, /!\[.*?\]\(.*?\)/,
  ];
  return patterns.some(pattern => pattern.test(text));
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
          <div className='markdown-content' 
            style={{maxWidth: "800px", backgroundColor: "white", paddingRight: 10, paddingLeft: 10, paddingBottom: 5, paddingTop: 1 }}>
            <ReactMarkdown>{content}</ReactMarkdown>
          </div>
        ) : (
          <pre className='pre-format' style={{ maxWidth: "800px",  backgroundColor: "white"}}>{content}</pre>
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