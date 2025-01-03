import React, { useState } from 'react';

const JsonTreeView = ({ data, initialExpanded = true }) => {
    const [isExpanded, setIsExpanded] = useState(initialExpanded);

    const getDataType = (value) => {
        if (Array.isArray(value)) return 'array';
        if (value === null) return 'null';
        return typeof value;
    };

    const renderValue = (value) => {
        const type = getDataType(value);

        switch (type) {
            case 'object':
                if (value === null) return <span className="json-null">null</span>;
                return (
                    <JsonTreeView 
                        data={value} 
                        initialExpanded={false}
                    />
                );
            case 'array':
                return (
                    <JsonTreeView 
                        data={value} 
                        initialExpanded={false}
                    />
                );
            case 'string':
                return <span className="json-string">"{value}"</span>;
            case 'number':
                return <span className="json-number">{value}</span>;
            case 'boolean':
                return <span className="json-boolean">{value.toString()}</span>;
            case 'null':
                return <span className="json-null">null</span>;
            default:
                return <span>{String(value)}</span>;
        }
    };

    const toggleExpand = () => {
        setIsExpanded(!isExpanded);
    };

    if (typeof data !== 'object' || data === null) {
        return renderValue(data);
    }

    const isArray = Array.isArray(data);
    const items = isArray ? data : Object.entries(data);

    return (
        <div className="json-tree-view">
            <span 
                className="json-toggle" 
                onClick={toggleExpand}
            >
                {isExpanded ? '▼' : '▶'} 
                {isArray ? '[' : '{'}
            </span>
            {isExpanded && (
                <div className="json-children">
                    {isArray ? (
                        items.map((item, index) => (
                            <div key={index} className="json-item">
                                {renderValue(item)}
                                {index < items.length - 1 && ','}
                            </div>
                        ))
                    ) : (
                        items.map(([key, value], index) => (
                            <div key={key} className="json-item">
                                <span className="json-key">{key}:</span>{' '}
                                {renderValue(value)}
                                {index < items.length - 1 && ','}
                            </div>
                        ))
                    )}
                </div>
            )}
            <span>{isArray ? ']' : '}'}</span>
        </div>
    );
};

export default JsonTreeView; 