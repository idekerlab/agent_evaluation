import { Link, useLocation } from "react-router-dom"


const ReviewList = ({type, analysisRuns, rankings, ...props}) => {
    const location = useLocation()

    let completeAnalysisRunIds = []
    rankings.map(ranking => {
        if (ranking.status == "complete")
            completeAnalysisRunIds.push(ranking.analysis_run_id) 
    })

    let analysisRunsToDisplay = []
    if (type == "complete") {
        analysisRuns.map(run => {
            if (completeAnalysisRunIds.includes(run.object_id))
                analysisRunsToDisplay.push(run)
        })
    } else {
        analysisRuns.map(run => {
            if (!completeAnalysisRunIds.includes(run.object_id))
                analysisRunsToDisplay.push(run)
        })
    }
    



    return (
        <div>
            <h2>
                {type == "complete" ? "Complete" : "Pending"} Review List
            </h2>
            <div>
                {analysisRunsToDisplay.map(analysisRun => (
                    <div key={analysisRun.object_id}>
                        <Link to={`${location.pathname}/${analysisRun.object_id}`}>{analysisRun.properties.name == "" ? `unnamed - ${analysisRun.object_id}` : analysisRun.properties.name}</Link>
                    </div>

                ))}
            </div>
        </div>
    )
}

export default ReviewList