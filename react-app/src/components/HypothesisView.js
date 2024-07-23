import { AgGridReact } from 'ag-grid-react' // React Data Grid Component
import HypothesisReviewForm from './HumanReviewForm'

const HypothesisView = ({hypothesis, dataset, index, numHypotheses, review, handleReviewChange, handleNextHypothesis, ...props}) => {

    let colDefs = []
    let rowData = []

    hypothesis.data.map((row, index) => {
        if (index == 0) {
            row.map(label => {
                colDefs.push({ field: label })
            })
        } else {
            let newRow = {}
            row.map((value, index) => {
                newRow[`${colDefs[index]["field"]}`] =  value
            })
            rowData.push(newRow)
        }
    })


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
            
            <HypothesisReviewForm review={review} handleReviewChange={handleReviewChange} />
            <p>
                <b>biological context:</b> {hypothesis.biological_context}
            </p>
            <p className='highlight'>
                <b>hypothesis:</b> {hypothesis.hypothesis_text}
            </p>
            <div className="ag-theme-quartz" style={{ height: 500 }} >
                <AgGridReact
                    rowData={rowData}
                    columnDefs={colDefs}
                />
            </div>
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