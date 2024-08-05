import HypothesisReviewForm from './HumanReviewForm'
import DataViewer from './DataViewer'


const HypothesisView = ({hypothesis, dataset, index, numHypotheses, rank, handleRankingChange, handleNextHypothesis, disableForm, ...props}) => {    


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
            <p className='highlight'>
                <b>hypothesis:</b> {hypothesis.hypothesis_text}
            </p>

            <DataViewer data={hypothesis.data} />

            <p>
                <b>data description:</b> {dataset.description}
            </p>
            <p>
                <b>experiment description:</b> {dataset.experiment_description}
            </p>
        </div>
    )
}

export default HypothesisView