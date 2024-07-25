import { useState, useEffect } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { api_base } from '../helpers/constants'
import HypothesisView from './HypothesisView'

const HypothesisList = ({analysisRuns, user, savedReviews, setReload, ...props}) => {
    const { objectId } = useParams()
    const [loading, setLoading] = useState(true)
    const [analysisRun, setAnalysisRun] = useState(null)
    const [hypotheses, setHypotheses] = useState([])
    const [datasets, setDatasets] = useState([])
    const [reviews, setReviews] = useState([])
    const [hypothesisIndex, setHypothesisIndex] = useState(0)
    const [alreadySavedData, setAlreadySavedData] = useState({})
    const navigate = useNavigate()

    const hasSavedReview = Object.keys(alreadySavedData).length > 0
    const disableForm = hasSavedReview ? alreadySavedData.status == "complete" : false
    

    useEffect(() => {
        fetchAnalysisRun()
    }, [analysisRuns])

    useEffect(()=> {
        if (!loading)
            initializeReviewData()
    }, [loading, hypotheses])

    const initializeReviewData = () => {
        let saved = savedReviews.find(review=> review.analysis_run_id == objectId)

        if (saved) {
            setAlreadySavedData(saved)
            setReviews(saved.reviews)
        } else {
            setReviews(hypotheses.map(_=> ({rating: null, comments: ""})))
        }
    }

    const fetchAnalysisRun = () => {
        axios.get(api_base+`/objects/analysisRun/${objectId}`)
            .then(response => {
                // Handle the response data
                // console.log(response)
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

    const handleSave = (statusStr, hasUndone=false) => {
        let review_str =  JSON.stringify({user_id: user.object_id, status: statusStr, reviews: reviews})

        let submitPath = api_base + `/objects/review/blank/new`
        let submitObj = {review_text: review_str, analysis_run_id: analysisRun.object_id}

        if (hasSavedReview) {
            submitPath = api_base + `/objects/review/${alreadySavedData.object_id}/edit`
            submitObj.object_id = alreadySavedData.object_id
        }
        

        axios.post(submitPath, submitObj, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            })
            .then(response => {
                console.log(response);
                setReload(prev => !prev)
                if (hasUndone)
                    navigate(`/my_reviews/${statusStr}/${objectId}`)
                else
                    navigate(`/my_reviews/${statusStr}`)
            })
            .catch(error => {
                console.error('Error:', error.message)
            })
    }

    const handleSubmit = () => {
        handleSave("complete")
    }

    const handleUndoSubmission = () => {
        handleSave("pending", true)
    }

    return (
        <div>
            { loading ? (
                <p>loading</p>
            ) : (
                <div>
                    { hypotheses && hypotheses.length > 0 ? (
                        <>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                                <h2>Review of {analysisRun.name}</h2>
                                { disableForm ?
                                        <button className='button' style={{backgroundColor: "grey"}} onClick={handleUndoSubmission}>Undo Submission</button>
                                    :
                                    <>
                                        <button className='button' style={{backgroundColor: "grey"}} onClick={()=>handleSave("pending")}>Save</button>
                                        <button className='button' style={{backgroundColor: "green"}} onClick={handleSubmit}>Submit</button>
                                    </>

                                }
                                
                            </div>
                            { reviews.length > 0 &&
                                <HypothesisView 
                                    hypothesis={hypotheses[hypothesisIndex]} 
                                    dataset={datasets[hypothesisIndex]} 
                                    index={hypothesisIndex} 
                                    numHypotheses={hypotheses.length} 
                                    review={reviews[hypothesisIndex]}
                                    handleReviewChange={(newReview) => handleReviewsChange(newReview, hypothesisIndex)}
                                    handleNextHypothesis={handleNextHypothesis}
                                    disableForm={disableForm}
                                />
                            }
                            
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