import { useState, useEffect } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { api_base } from '../helpers/constants'
import HypothesisView from './HypothesisView'

const HypothesisList = ({analysisRuns, user, savedRankings, setReload, ...props}) => {

    const { objectId } = useParams()
    const [loading, setLoading] = useState(true)
    const [analysisRun, setAnalysisRun] = useState(null)
    const [hypotheses, setHypotheses] = useState([])
    const [datasets, setDatasets] = useState([])
    const [ranking, setRanking] = useState({})
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
        let saved = savedRankings.find(review=> review.analysis_run_id == objectId)

        if (saved) {
            setAlreadySavedData(saved)
            setRanking(saved.ranking)
        } else {
            let newRanking = {}
            hypotheses.map((hypo, index)=> {
                newRanking[hypo.object_id] = {stars: null, comments: "", order: index+1}
            })
            setRanking(newRanking)
        }
    }
    const fetchAnalysisRun = () => {
        axios.get(api_base+`/objects/analysisRun/${objectId}`)
            .then(response => {
                // Handle the response data
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

    const handleRankingChange = (newRank, hypothesisId) => {
        let newRankings = {...ranking}
        newRankings[hypothesisId] = newRank
        setRanking(newRankings)
    }

    const handleSave = (statusStr, hasUndone=false) => {
        let review_str =  JSON.stringify({user_id: user.object_id, status: statusStr, ranking: ranking})

        let submitPath = api_base + `/objects/review/blank/new`
        let submitObj = {ranking_data: review_str, analysis_run_id: analysisRun.object_id}

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
        let hasRankedAllHypotheses = true
        Object.keys(ranking).map(key => {
            let rank = ranking[key]
            if (rank.stars == null)
                hasRankedAllHypotheses = false
        })

        if (hasRankedAllHypotheses)
            handleSave("complete")
        else
            alert("Please assign stars to all hypotheses to submit.")
    }

    const handleUndoSubmission = () => {
        handleSave("pending", true)
    }

    const getOrderedRanks = () => {
        let ranks = []

        Object.keys(ranking).map(key => {
            let rank = ranking[key]
            ranks.push(rank)
        })

        ranks.sort((a,b) => b.stars - a.stars)
        return (
            <ul>
                {ranks.map(rank => (
                    <li>Hypothesis {rank.order}, stars {rank.stars ? '*'.repeat(rank.stars) + ` (${rank.stars})` : "-"}</li>
                ))}
            </ul>
        )
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
                                <div style={{ position: 'absolute', right: 70 }}>
                                    {getOrderedRanks()}
                                </div>
                            </div>
                            { Object.keys(ranking).length > 0 &&
                                <HypothesisView 
                                    hypothesis={hypotheses[hypothesisIndex]} 
                                    dataset={datasets[hypothesisIndex]} 
                                    index={hypothesisIndex} 
                                    numHypotheses={hypotheses.length} 
                                    rank={ranking[hypotheses[hypothesisIndex].object_id]}
                                    handleRankingChange={(newRank) => handleRankingChange(newRank, hypotheses[hypothesisIndex].object_id)}
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