import HypothesisReviewForm from './HumanReviewForm'
import DataViewer from './DataViewer'
import { useState } from 'react'
import GeneSymbolReference from './GeneSymbolReference'

const HypothesisView = ({hypothesis, dataset, index, numHypotheses, rank, handleRankingChange, handleNextHypothesis, disableForm, ...props}) => {
    const [iframeSrc, setIframeSrc] = useState('')
    
    const areAllLettersUpperCase = (str) => {
        // Remove non-letter characters from the string
        const lettersOnly = str.replace(/[^a-zA-Z]/g, '')
        
        // Check if the remaining letters are all uppercase
        return lettersOnly.length > 0 && lettersOnly === lettersOnly.toUpperCase()
    }

    const enhanceGeneSymbols = (textArr, symbols) => {
        let hypoArr = []
        
        textArr.map(str => {
            if (symbols.includes(str)) {
                hypoArr.push(
                    // <a href={`https://www.genenames.org/tools/search/#!/?query=${str}`} >{str}</a>
                    <span 
                        key={str}
                        style={{ color: 'blue', cursor: 'pointer' }}
                        onClick={() => setIframeSrc(`https://www.genenames.org/tools/search/#!/?query=${str}`)}
                    >
                        {str}
                    </span>
                )
            } else {
                hypoArr.push(str)
            }
        })
        return hypoArr.map((text, index) => (<>{text}{index < hypoArr.length - 1 && ' '}</>))
    }

    const hypothesisTextDisplay = (text) => {
        let textArr = text.split(' ')

        let geneSymbols = textArr.filter(str => areAllLettersUpperCase(str))

        let enhancedText = enhanceGeneSymbols(textArr, geneSymbols)
        

        return (
            <p className='highlight'>
                <b>hypothesis:</b> {enhancedText}
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
                <GeneSymbolReference iframeSrc={iframeSrc} closeIframe={() => setIframeSrc("")} />
            )}
        </div>
    )
}

export default HypothesisView