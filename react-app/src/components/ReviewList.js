import { Link, useLocation } from "react-router-dom"

const ReviewList = ({analysisRuns, ...props}) => {
    const location = useLocation()

    return (
        <div>
            <h2>Review List</h2>
            <div>
                {analysisRuns.map(analysisRun => (
                    <>
                        <Link to={`${location.pathname}/${analysisRun.object_id}`}>{analysisRun.properties.name}</Link>
                        <br/>
                    </>
                ))}
            </div>
        </div>
    )
}

export default ReviewList