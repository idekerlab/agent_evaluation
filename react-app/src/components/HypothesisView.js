import React, { useState } from 'react'
import HypothesisReviewForm from './HumanReviewForm'
import DataViewer from './DataViewer'
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
        if (!hypothesis || !text) return null;
        
        let geneSymbols = hypothesis.gene_symbols
        let enhancedHypothesisText = addLinksToHypothesis(text, geneSymbols)

        return (
            <pre className='focus-area pre-format2'>
                <b>hypothesis:</b> {enhancedHypothesisText}
            </pre>
        )
    }

    if (!hypothesis) {
        return <div>No hypothesis data available</div>
    }

    return (
        <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
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

            <div style={{ display: 'flex', minHeight: '400px', margin: '20px 0' }}>
                <div style={{ width: '800px', minWidth: '500px', padding: '16px', overflowY: 'auto', borderRight: '1px solid #ccc' }}>
                    {hypothesisTextDisplay(hypothesis.hypothesis_text)}
                    {hypothesis.biological_context && (
                        <pre className='pre-format2'>
                            <b>biological context:</b> {hypothesis.biological_context}
                        </pre>
                    )}
                    {dataset && (
                        <>
                            <pre className='pre-format2'>
                                <b>data description:</b> {dataset.description}
                            </pre>
                            <pre className='pre-format2'>
                                <b>experiment description:</b> {dataset.experiment_description}
                            </pre>
                        </>
                    )}
                </div>
                <div style={{ flexGrow: 1, minWidth: '500px', padding: '16px', overflowY: 'auto' }}>
                    {hypothesis.data && <DataViewer data={hypothesis.data} />}
                </div>
            </div>

            {iframeSrc && (
                <FriendlyIFrame iframeSrc={iframeSrc} closeIframe={() => setIframeSrc("")} />
            )}
        </div>
    )
}

export default HypothesisView
