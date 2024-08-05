import React, { useState, useEffect } from 'react'
import { Link, useParams, useNavigate, NavLink } from 'react-router-dom'
import axios from 'axios'
import { api_base } from '../helpers/constants'
import DataViewer from './DataViewer'

const ObjectView = ({objectType, ...props}) => {
    const { objectId } = useParams()
    const navigate = useNavigate()

    const [loading, setLoading] = useState(true)
    const [executing, setExecuting] = useState(false)
    const [object, setObject] = useState({})
    const [objectSpec, setObjectSpec] = useState({})
    const [linkNames, setLinkNames] = useState([])

    useEffect(() => {
        getObject()
    }, [objectId])

    const getObject = () => {
        axios.get(api_base+`/objects/${objectType}/${objectId}`)
          .then(response => {
            // Handle the response data
            // console.log(response)
            setObject(response.data.object)
            setObjectSpec(response.data.object_spec)
            setLinkNames(response.data.link_names)
            setLoading(false)
          })
          .catch(error => {
            // Handle any errors
            alert(error)
            setLoading(false)
          })
      }

      const executePlan = () => {
        setExecuting(true)
        
        axios.post(api_base+`/objects/${objectType}/${objectId}/execute`)
            .then(response => {
                // Handle the response data
                console.log(response)
                navigate(response.data.url)
                setExecuting(false)
            })
            .catch(error => {
                // Handle any errors
                alert(error)
                setExecuting(false)
            })
      }

      const deleteObject = () => {
        axios.post(`${api_base}/objects/${objectType}/${objectId}/delete`)
            .then(response=> {
                navigate(`/${objectType}`)
            })
            .catch(error => {
                alert(error)
            })
      }

      const cloneObject = () => {
        axios.get(`${api_base}/objects/${objectType}/${objectId}/clone`)
            .then(response=> {
                navigate(`/${objectType}/${response.data.object_id}`)
            })
            .catch(error => {
                alert(error)
            })
      }

    return (
        <div>
            { loading ? 
                <p>Loading...</p>
                :
                <div>
                    <div className="header">
                        <img
                            src={`/static/images/${objectType}.png`}
                            alt={`${objectType} Logo`}
                        />
                        <div>
                            <h1>
                                {objectType} : {object.name || "unnamed"}
                            </h1>
                            {object.object_id ? (
                                <>
                                    <p>ID: {object.object_id}</p>
                                    <p>Created: {object.created}</p>
                                </>
                            ) : (
                                <p>No object data available.</p>
                            )}
                        </div>
                        <div style={{ marginLeft: "auto" }}>
                            {(objectType === "analysis_plan" || objectType === "review_plan") &&
                                <button
                                    className="button spaced-button"
                                    style={{ backgroundColor: "rgb(42, 138, 0)" }}
                                    onClick={executePlan}
                                >
                                    { !executing ? 
                                        "Execute"
                                    :
                                        <i className="fa-solid fa-spinner fa-spin-pulse fa-lg"></i>
                                    }
                                    
                                </button>
                            }
                            <Link className="button spaced-button" to={`/${objectType}/${objectId}/edit`}  >
                                Edit
                            </Link>
                            <button className="button spaced-button" onClick={cloneObject} >
                                Clone
                            </button>
                            <button className="button spaced-button" style={{ backgroundColor: "crimson" }} onClick={deleteObject} >
                                Delete
                            </button>
                        </div>
                    </div>
                    <div className="main-content">
                    {object && objectSpec && objectSpec.properties ? (
                        <table style={{borderCollapse: 'collapse'}}>
                        <tbody>
                            {Object.entries(objectSpec.properties).map(
                            ([propName, propSpec]) =>
                                propName !== "object_id" &&
                                propName !== "created" &&
                                propName !== "name" && (
                                <tr key={propName}>
                                    <td
                                    style={{
                                        width: "100px",
                                        minWidth: "100px",
                                        wordWrap: "break-word",
                                        paddingTop: "20px",
                                        textAlign: "right",
                                        border: 'none'
                                    }}
                                    >
                                    {propSpec.label || propName}
                                    </td>
                                    <td style={{ overflowX: "scroll", border: 'none'}}>
                                    {propSpec.view === "scrolling_table" ? (
                                        <DataViewer data={object[propName]} />
                                    ) : propSpec.view === "list_of_object_links" &&
                                        object[propName] ? (
                                        <p
                                        style={{ maxWidth: "800px" }}
                                        className="property-container"
                                        >
                                        {object[propName].map((objectId) => (
                                            <React.Fragment key={objectId}>
                                            {linkNames[objectId]} -{" "}
                                            <Link
                                                to={`/${propSpec.object_type}/${objectId}`}
                                            >
                                                {objectId}
                                            </Link>
                                            <br />
                                            </React.Fragment>
                                        ))}
                                        </p>
                                    ) : propSpec.view === "object_link" &&
                                        object[propName] ? (
                                        <p
                                        style={{ maxWidth: "800px" }}
                                        className="property-container"
                                        >
                                        {linkNames[object[propName]]} -{" "}
                                        <Link
                                            to={`/${propSpec.object_type}/${object[propName]}`}
                                        >
                                            {object[propName]}
                                        </Link>
                                        </p>
                                    ) : (
                                        <pre style={{ maxWidth: "800px" }}>
                                        {object[propName]}
                                        </pre>
                                    )}
                                    </td>
                                </tr>
                                )
                            )}
                        </tbody>
                        </table>
                    ) : (
                        <p>No properties available.</p>
                    )}
                    </div>
                </div>
            }
        </div>
       
    )
}

export default ObjectView