import { useState, useEffect } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import HypothesisView from './HypothesisView'

const api_base = process.env.REACT_APP_API_BASE_URL

const HypothesisList = ({runId, analysisRuns, user, savedRankings, setReload, viewOnly, ...props}) => {

    const { objectId } = useParams()
    const analysisRunId = runId ? runId : objectId
    const [loading, setLoading] = useState(true)
    const [analysisRun, setAnalysisRun] = useState(null)
    const [hypotheses, setHypotheses] = useState([])
    const [datasets, setDatasets] = useState([])
    const [ranking, setRanking] = useState({})
    const [hypothesisIndex, setHypothesisIndex] = useState(0)
    const [errorMessage, setErrorMessage] = useState("")
    const [successMessage, setSuccessMessage] = useState("")

    const [alreadySavedData, setAlreadySavedData] = useState({})
    const navigate = useNavigate()

    const hasSavedReview = Object.keys(alreadySavedData).length > 0
    const disableForm = viewOnly ? true : (hasSavedReview ? alreadySavedData.status == "complete" : false)
    

    useEffect(() => {
        fetchAnalysisRun()
    }, [analysisRuns])

    useEffect(()=> {
        if (!loading) {
            initializeReviewData()
            // Reset hypothesis index if it's out of bounds
            if (hypothesisIndex >= hypotheses.length) {
                setHypothesisIndex(0)
            }
        }
    }, [loading, hypotheses])

    const initializeReviewData = () => {
        let saved = savedRankings.find(review=> review.analysis_run_id == analysisRunId)

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
    const fetchAnalysisRun = async () => {
        try {
            const response = await axios.get(api_base+`/objects/analysis_run/${analysisRunId}`);
            const analysisRun = response.data.object;
            setAnalysisRun(analysisRun);
            if (analysisRun && analysisRun.hypothesis_ids) {
                await fetchHypotheses(analysisRun.hypothesis_ids);
            } else {
                setErrorMessage('No hypotheses found in this analysis run');
                setLoading(false);
            }
        } catch (error) {
            console.error('Error fetching analysis run:', error);
            setErrorMessage('Failed to load analysis run. Please try again.');
            setLoading(false);
        }
    }

    const fetchHypotheses = async (hypothesis_ids) => {
        try {
            const hypothesesPromises = hypothesis_ids.map(id => 
                axios.get(`${api_base}/objects/hypothesis/${id}`)
                    .then(response => response.data.object)
                    .catch(error => {
                        console.warn(`Failed to fetch hypothesis ${id}:`, error);
                        return null;
                    })
            );
            const newHypotheses = (await Promise.all(hypothesesPromises)).filter(Boolean);
            setHypotheses(newHypotheses);

            if (newHypotheses.length > 0) {
                const datasetIds = newHypotheses.map(hypo => hypo.dataset_id).filter(Boolean);
                await fetchDatasets(datasetIds);
            } else {
                setErrorMessage('No hypotheses could be loaded');
                setLoading(false);
            }
        } catch (error) {
            console.error('Error fetching hypotheses:', error);
            setErrorMessage('Failed to load hypotheses. Please try again.');
            setLoading(false);
        }
    }

    const fetchDatasets = async (datasetIds) => {
        try {
            const datasetPromises = datasetIds.map(id => 
                axios.get(`${api_base}/objects/dataset/${id}`)
                    .then(response => response.data.object)
                    .catch(error => {
                        console.warn(`Failed to fetch dataset ${id}:`, error);
                        return null;
                    })
            );
            const newDatasets = await Promise.all(datasetPromises);
            setDatasets(newDatasets);
            if (newDatasets.some(d => d === null)) {
                setErrorMessage('Some datasets could not be loaded');
            }
        } catch (error) {
            console.error('Error fetching datasets:', error);
            setErrorMessage('Failed to load some datasets');
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

    const handleSave = async (statusStr, hasUndone=false) => {
        try {
            if (!user || !analysisRun) {
                setErrorMessage('Missing user or analysis run data');
                return;
            }

            const review_str = JSON.stringify({
                user_id: user.object_id,
                status: statusStr,
                ranking: ranking
            });

            const submitPath = hasSavedReview 
                ? api_base + `/objects/review/${alreadySavedData.object_id}/edit`
                : api_base + `/objects/review/blank/new`;

            const submitObj = {
                ranking_data: review_str,
                analysis_run_id: analysisRun.object_id,
                name: `${user.properties.name}'s review of ${analysisRun.name}`
            };

            if (hasSavedReview) {
                submitObj.object_id = alreadySavedData.object_id;
            }

            await axios.post(submitPath, submitObj, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            });

            setSuccessMessage('Review saved successfully');
            setTimeout(() => setSuccessMessage(""), 3000);
            setReload(prev => !prev);
            // Short delay before navigation to show success message
            setTimeout(() => {
                navigate(`/my_reviews/${statusStr}${hasUndone ? `/${objectId}` : ''}`);
            }, 1000);
        } catch (error) {
            console.error('Error saving review:', error);
            setErrorMessage('Failed to save review. Please try again.');
            setTimeout(() => setErrorMessage(""), 5000);
        }
    }

    const handleSubmit = () => {
        const unrankedHypotheses = Object.values(ranking).filter(rank => rank.stars === null);
        
        if (unrankedHypotheses.length === 0) {
            handleSave("complete");
        } else {
            setErrorMessage('Please assign stars to all hypotheses to submit.');
            setTimeout(() => setErrorMessage(""), 5000);
        }
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
            <ul style={{ fontSize: '12px' }}>
                {ranks.map((rank, index) => (
                    <li key={`${index}-rank`}>Hypothesis {rank.order}, stars {rank.stars ? '*'.repeat(rank.stars) + ` (${rank.stars})` : "-"}</li>
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
                    {errorMessage && (
                        <div style={{ 
                            padding: '10px', 
                            marginBottom: '10px', 
                            backgroundColor: '#ffebee', 
                            color: '#c62828',
                            borderRadius: '4px'
                        }}>
                            {errorMessage}
                        </div>
                    )}
                    {successMessage && (
                        <div style={{ 
                            padding: '10px', 
                            marginBottom: '10px', 
                            backgroundColor: '#e8f5e9', 
                            color: '#2e7d32',
                            borderRadius: '4px'
                        }}>
                            {successMessage}
                        </div>
                    )}

                    { hypotheses && hypotheses.length > 0 ? (
                        <>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                                <h3>Review of {analysisRun.name == "" ? "unnamed" : analysisRun.name}</h3>

                                { !viewOnly &&
                                    <>
                                        { disableForm ?
                                            <button className='button' style={{backgroundColor: "grey"}} onClick={handleUndoSubmission}>Undo Submission</button>
                                            :
                                            <>
                                                <button className='button' style={{backgroundColor: "grey"}} onClick={()=>handleSave("pending")}>Save</button>
                                                <button className='button' style={{backgroundColor: "green"}} onClick={handleSubmit}>Submit</button>
                                            </>
                                        }
                                    </>
                                }
                                
                                <div>
                                    {getOrderedRanks()}
                                </div>
                            </div>
                            { Object.keys(ranking).length > 0 && hypotheses[hypothesisIndex] && (
                                <HypothesisView 
                                    hypothesis={hypotheses[hypothesisIndex]} 
                                    dataset={datasets[hypothesisIndex] || null} 
                                    index={hypothesisIndex} 
                                    numHypotheses={hypotheses.length} 
                                    rank={ranking[hypotheses[hypothesisIndex].object_id] || {}}
                                    handleRankingChange={(newRank) => handleRankingChange(newRank, hypotheses[hypothesisIndex].object_id)}
                                    handleNextHypothesis={handleNextHypothesis}
                                    disableForm={disableForm}
                                />
                            )}

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
