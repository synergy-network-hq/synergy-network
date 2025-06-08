import React, { useState } from 'react';
import '../styles/docs.css';

const DocSearchBar = () => {
  const [query, setQuery] = useState('');

  const handleSearch = () => {
    if (query.trim()) {
      console.log(`Searching for: ${query}`);
      // Later: emit query to search engine or parent component
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="doc-searchbar">
      <input
        type="text"
        id="search"
        placeholder="Search documentation..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
      />
      <button className="doc-search-button" onClick={handleSearch}>
        Search
      </button>
    </div>
  );
};

export default DocSearchBar;
