import HypothesisReviewForm from './HumanReviewForm'
import DataViewer from './DataViewer'
import React, { useState } from 'react'
import FriendlyIFrame from './FriendlyIFrame'
import { fetchIframeSrc } from '../helpers/iFrameHelpers'

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
                    onClick={() => fetchIframeSrc(part, setIframeSrc)}
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
            <pre className='focus-area pre-format2'>
                <b>hypothesis:</b> {enhancedHypothesisText}
            </pre>
        )
    }

    return (
        <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <h3>
                    Hypothesis {index + 1}/{numHypotheses}
                </h3>
                <button className='button' onClick={() => handleNextHypothesis("prev")}>
                    <i className="fa-solid fa-arrow-left-long fa-lg"></i> Previous
                </button>
                <button className='button' onClick={() => handleNextHypothesis("next")}>
                    Next <i className="fa-solid fa-arrow-right-long fa-lg"></i>
                </button>
            </div>

            <HypothesisReviewForm rank={rank} disableForm={disableForm} handleRankingChange={handleRankingChange} />

            <div className="flex flex-row min-h-screen">
                <div className="w-[800px] min-w-[500px] p-4 overflow-auto">
                    {hypothesisTextDisplay(hypothesis.hypothesis_text)}
                </div>
                <div className="flex-grow min-w-[500px] p-4 overflow-auto">
                    <DataViewer data={hypothesis.data} />
                </div>
            </div>

            <pre className='pre-format2'>
                <b>biological context:</b> {hypothesis.biological_context}
            </pre>


            <pre className='pre-format2'>
                <b>data description:</b> {dataset.description}
            </pre>
            <pre className='pre-format2'>
                <b>experiment description:</b> {dataset.experiment_description}
            </pre>
            {iframeSrc && (
                <FriendlyIFrame iframeSrc={iframeSrc} closeIframe={() => setIframeSrc("")} />
            )}
        </div>
    )
}

export default HypothesisView