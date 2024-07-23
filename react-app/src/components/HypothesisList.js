import { useState, useEffect } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { api_base } from '../helpers/constants'
import HypothesisView from './HypothesisView'

const HypothesisList = ({analysisRuns, ...props}) => {
    const { objectId } = useParams()
    const [loading, setLoading] = useState(true)
    const [analysisRun, setAnalysisRun] = useState(null)
    const [hypotheses, setHypotheses] = useState([])
    const [datasets, setDatasets] = useState([])
    const [reviews, setReviews] = useState([])
    const [hypothesisIndex, setHypothesisIndex] = useState(0)
    const navigate = useNavigate()
    // const analysisRun = analysisRuns.find(run => run.objectId == objectId)

    useEffect(() => {
        fetchAnalysisRun()
        
    }, [analysisRuns])

    const fetchAnalysisRun = () => {
        axios.get(api_base+`/objects/analysisRun/${objectId}`)
            .then(response => {
                // Handle the response data
                console.log(response)
                const analysisRun = response.data.object
                setAnalysisRun(analysisRun)
                fetchHypotheses(analysisRun.hypothesis_ids)
                // setObjectSpec(response.data.object_spec)
                // setLinkNames(response.data.link_names)
                // setLoading(false)
            })
            .catch(error => {
                // Handle any errors
                alert(error)
                // setLoading(false)
            })
    }

    const fetchHypotheses = async (hypothesis_ids) => {
        try {
            const hypothesesResponses = await Promise.all(
            hypothesis_ids.map(id => axios.get(`${api_base}/objects/hypothesis/${id}`))
            );
            const newHypotheses = hypothesesResponses.map(response => response.data.object)
            setHypotheses(newHypotheses);

            setReviews(newHypotheses.map(_=> ({rating: null, comments: ""})))

            const datasetIds = newHypotheses.map(hypo => hypo.dataset_id)
            fetchDatasets(datasetIds)

        } catch (error) {
            alert(error);
        } finally {
        //   setLoading(false);
        }
    }

    const fetchDatasets = async (datasetIds) => {
        try {
            const datasetResponses = await Promise.all(
                datasetIds.map(id => axios.get(`${api_base}/objects/dataset/${id}`))
            );
            const newDatasets = datasetResponses.map(response => response.data.object);
            setDatasets(newDatasets);
        } catch (error) {
            alert(error);
        } finally {
            setLoading(false);
        }
    }

    const handleNextHypothesis = (direction) => {
        if (direction == "next") {
            if (hypothesisIndex + 1 == hypotheses.length)
                setHypothesisIndex(0)
            else
                setHypothesisIndex(prev => (prev + 1))
        } else if (direction == "prev") {
            if (hypothesisIndex == 0)
                setHypothesisIndex(hypotheses.length - 1)
            else
                setHypothesisIndex(prev => (prev - 1))
        }
    }

    const handleReviewsChange = (newReview, index) => {
        let newReviews = [...reviews]
        newReviews[index] = newReview
        setReviews(newReviews)
    }

    return (
        <div>
            { loading ? (
                <p>loading</p>
            ) : (
                <div>
                    
                    {/* <button onClick={()=>navigate(-1)}>Back</button> */}
                    { hypotheses && hypotheses.length > 0 ? (
                        <>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                                <h2>Review of {analysisRun.name}</h2>
                                <button className='button' style={{backgroundColor: "grey"}}>Save</button>
                                <button className='button' style={{backgroundColor: "green"}}>Submit</button>
                            </div>
                            <HypothesisView 
                                hypothesis={hypotheses[hypothesisIndex]} 
                                dataset={datasets[hypothesisIndex]} 
                                index={hypothesisIndex} 
                                numHypotheses={hypotheses.length} 
                                review={reviews[hypothesisIndex]}
                                handleReviewChange={(newReview) => handleReviewsChange(newReview, hypothesisIndex)}
                                handleNextHypothesis={handleNextHypothesis}
                            />
                        </>
                        
                    ) : (
                        <p>No hypotheses available</p>
                    )}
                </div>
            )}
        </div>
    )
}

export default HypothesisList