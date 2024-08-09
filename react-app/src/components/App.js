import React, { useState, useEffect } from 'react'
import { Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import axios from 'axios'
import TopBar from './TopBar'
import Sidebar from './Sidebar'
import ObjectList from './ObjectList'
import ObjectView from './ObjectView'
import ObjectForm from './ObjectForm'
import ReviewPortal from './ReviewPortal'
import { api_base } from '../helpers/constants'

const App = () => {
  const location = useLocation()

  const [loading, setLoading] = useState(true)
  const [objectSpecs, setObjectSpecs] = useState("")
  const [users, setUsers] = useState([])

  const inReviewPortal = `${location.pathname}`.includes("my_reviews")

  let objectTypes = null
  if (!loading) {
    objectTypes = Object.keys(objectSpecs)
  }

  useEffect(() => {
    getObjectSpecs()
    getUsers()
  }, [])

  const getObjectSpecs = () => {
    axios.get(api_base+'/get_object_specs')
      .then(response => {
        // Handle the response data
        setObjectSpecs(response.data)
        setLoading(false)
      })
      .catch(error => {
        // Handle any xvzz
        alert(error)
        // setError(error)
        setLoading(false)
      })
  }

  const getUsers = () => {
    axios.get(api_base+'/objects/user')
      .then(response => {
        // Handle the response data
        setUsers(response.data.objects)
        // setLoading(false)
      })
      .catch(error => {
        // Handle any xvzz
        alert(error)
        // setError(error)
        // setLoading(false)
      })
  }

  return (
    <div>
      <TopBar />
      { !loading &&
        <div className="container">
          {!inReviewPortal && <Sidebar objectTypes={objectTypes} />}
          <div className={inReviewPortal ? "content" : "content"}>
            <Routes>
              {objectTypes.map((type, index) => (
                <React.Fragment key={`${index}-routes`}>
                  <Route 
                    exact 
                    path={`/${type}`} 
                    element={<ObjectList specs={objectSpecs[type]} objectType={type} />} 
                    key={`${index}-r1`} 
                  />
                  <Route 
                    path={`/${type}/:objectId`} 
                    element={<ObjectView specs={objectSpecs[type]} objectType={type} />} 
                    key={`${index}-r2`} 
                  />
                  <Route
                    path={`/${type}/:objectId/edit`} 
                    element={<ObjectForm specs={objectSpecs[type]} objectType={type} formType="edit" />} 
                    key={`${index}-r3`} 
                  />
                  <Route 
                    path={`/${type}/new`} 
                    element={<ObjectForm specs={objectSpecs[type]} objectType={type} formType="new" />} 
                    key={`${index}-r5`} 
                  />
                </React.Fragment>
                
              ))}
              <Route path={`/my_reviews/*`} element={<ReviewPortal />} />
              <Route exact path="/" element={<Welcome />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </div>
        </div> 
      }
    </div>
  )
}

const Welcome = () => {
  const navigate = useNavigate()

  return (
    <div className='content'>
      <h1>Welcome to Deckard, Your LLM Companion to Scientific Discovery</h1>
      <h2>
        Select a resource on the side to get started.
      </h2>
      <button className='button' onClick={() => navigate("/my_reviews/home")}>
        Go to Review Portal
      </button>
    </div>
  )
}

const NotFound = () => {
  return (
    <h1>Resource not found</h1>
  )
}

export default App
