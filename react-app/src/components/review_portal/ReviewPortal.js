import React, { useState, useEffect } from 'react'
import { Route, Routes, useLocation, useNavigate, NavLink } from 'react-router-dom'
import ReviewerLogin from './ReviewerLogin'
import ReviewList from './ReviewList'
import HypothesisList from '../friendly_hypotheses_display/HypothesisList'
import axios from 'axios'

const api_base = process.env.REACT_APP_API_BASE_URL

const ReviewPortal = () => {
    const navigate = useNavigate()
    const [loading, setLoading] = useState(true)

    const [reload, setReload] = useState(false)
    const [analysisRuns, setAnalysisRuns] = useState([])
    const [rankings, setRankings] = useState([])

    const [user, setUser] = useState(null)

    const getUserFromLocalStorage = () => {
        try {
            return JSON.parse(sessionStorage.getItem('user'))
        } catch (error) {
            return null
        }
    }
    useEffect(()=>{
        if (sessionStorage.getItem('user'))
            setUser(getUserFromLocalStorage())  
    }, [])

    useEffect(() => {
        getAnalysisRuns()

    }, [user, reload])


    const getAnalysisRuns = () => {
        axios.get(api_base+`/objects/analysis_run`)
            .then(response => {
                // Handle the response data
                // console.log(response)
                let runs = response.data.objects
                let filteredRuns = filterAnalysisRuns(runs)
                setAnalysisRuns(filteredRuns)

                getReviews()
                // setLoading(false)
            })
            .catch(error => {
                // Handle any errors
                alert(error)
                // setLoading(false)
            })
    }

    const getReviews = () => {
        axios.get(api_base+`/objects/review`)
            .then(response => {
                // Handle the response data
                // console.log(response)
                let reviews = response.data.objects
                let filteredReviews = filterReviews(reviews)
                // console.log(filteredReviews);
                setRankings(filteredReviews)

                setLoading(false)
            })
            .catch(error => {
                // Handle any errors
                alert(error)
                setLoading(false)
            })
    }


    const filterReviews = (reviews) => {
        if (user != null) {
            const filteredRuns = []
            reviews.filter(review => {
                // console.log(review.properties.review_text);
                if (isValidJSON(review.properties.ranking_data)) {
                    let rankingObj = JSON.parse(review.properties.ranking_data)
                    if (rankingObj.user_id == user.object_id) {
                        filteredRuns.push({...rankingObj, analysis_run_id: review.properties.analysis_run_id, object_id: review.object_id})
                        return true
                    }
                }
                return false
            })
            return filteredRuns
        }
        return []
    }

    const isValidJSON = (str) => {
        try {
            JSON.parse(str)
            return true
        } catch (e) {
            return false
        }
    }

    const filterAnalysisRuns = (analysisRuns) => {
        if (user != null) {
            const filteredRuns = analysisRuns.filter(run => (run.properties.user_ids ?? []).includes(user.object_id))
            return filteredRuns
        }
        return []
    }


    const getHypothesisList = () => {
        return <HypothesisList analysisRuns={analysisRuns} user={user} savedRankings={rankings} setReload={setReload} />
    }

    return (
        <div className="portal-content">
            <div className="sidebar">
                <h2 style={{textAlign: 'center'}}>Review Portal</h2>
                <NavLink to={`/my_reviews/home`}>
                    <button className='button' disabled={user == null}>Home</button>
                </NavLink>
                <NavLink to={`/my_reviews/pending`}>
                    <button className='button' disabled={user == null}>Pending Reviews</button>
                </NavLink>
                <NavLink to={`/my_reviews/complete`}>
                    <button className='button' disabled={user == null}>Complete Reviews</button>
                </NavLink>
            </div>

            <div className="main-content">
                <Routes>
                    { user != null &&
                        <>
                            <Route path={`/pending`} element={<ReviewList type="pending" analysisRuns={analysisRuns} rankings={rankings} />} />
                            <Route path={`/pending/:objectId`} element={getHypothesisList()} />
                            <Route path={`/complete`} element={<ReviewList type="complete" analysisRuns={analysisRuns} rankings={rankings} />} />
                            <Route path={`/complete/:objectId`} element={getHypothesisList()} />
                        </>
                    }
                    <Route path={`/*`} element={<ReviewerLogin user={user} setUser={(val)=>setUser(val)} />} />
                </Routes>
            </div>
        </div>
    )
}

export default ReviewPortal