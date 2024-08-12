import HypothesisReviewForm from './HumanReviewForm'
import DataViewer from './DataViewer'
import React, { useState } from 'react'
import FriendlyIFrame from './FriendlyIFrame'

const HypothesisView = ({hypothesis, dataset, index, numHypotheses, rank, handleRankingChange, handleNextHypothesis, disableForm, ...props}) => {
    const [iframeSrc, setIframeSrc] = useState('')

    const addLinksToHypothesis = (text, symbols) => {
        if (!text || !symbols || !Array.isArray(symbols)) {
            return text
        }
        
        let regexPattern = symbols.map(symbol => `\\${symbol}`).join('|')
        let regex = new RegExp(`(${regexPattern})`, 'g')
        
        return text.split(regex).map((part, index) => 
            symbols.includes(part) ? (
                <span 
                    key={`${part}-${index}`}
                    style={{ color: 'blue', cursor: 'pointer' }}
                    onClick={() => setIframeSrc(`https://www.ncbi.nlm.nih.gov/gene/?term=${part}`)}
                >
                    {part}
                </span>
            ) : part
        )
    }

    const hypothesisTextDisplay = (text) => {
        let geneSymbols = hypothesis.gene_symbols
        let enhancedHypothesisText = addLinksToHypothesis(text, geneSymbols)

        return (
            <p className='highlight'>
                <b>hypothesis:</b> {enhancedHypothesisText}
            </p>
        )
    }

    return (
        <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                <h2>
                    Hypothesis {index + 1}/{numHypotheses}
                </h2>
                <button className='button' onClick={() => handleNextHypothesis("prev")}>
                    <i className="fa-solid fa-arrow-left-long fa-lg"></i> Previous
                </button>
                <button className='button' onClick={() => handleNextHypothesis("next")}>
                    Next <i className="fa-solid fa-arrow-right-long fa-lg"></i>
                </button>
            </div>

            <HypothesisReviewForm rank={rank} disableForm={disableForm} handleRankingChange={handleRankingChange} />

            <p>
                <b>biological context:</b> {hypothesis.biological_context}
            </p>

            {hypothesisTextDisplay(hypothesis.hypothesis_text)}
            
            <DataViewer data={hypothesis.data} />

            <p>
                <b>data description:</b> {dataset.description}
            </p>
            <p>
                <b>experiment description:</b> {dataset.experiment_description}
            </p>
            {iframeSrc && (
                <FriendlyIFrame iframeSrc={iframeSrc} closeIframe={() => setIframeSrc("")} />
            )}
        </div>
    )
}

export default HypothesisView