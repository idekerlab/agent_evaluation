import React, { useState, useEffect } from 'react'
import { Link, useParams, useNavigate, NavLink } from 'react-router-dom'
import axios from 'axios'
import DataViewer from './DataViewer'
import SimpleSVGViewer from './SimpleSVGViewer';
import HypothesisList from './HypothesisList'
import MarkdownDisplay from './MarkdownDisplay';
import JsonTreeView from './JsonTreeView';

const OBJECT_SPEC_NAME = "_object_spec"
const api_base = process.env.REACT_APP_API_BASE_URL

const ObjectView = ({objectType, ...props}) => {
    const { objectId } = useParams()
    const navigate = useNavigate()

    const [loading, setLoading] = useState(true)
    const [executing, setExecuting] = useState(false)
    const [object, setObject] = useState({})
    const [objectSpec, setObjectSpec] = useState({})
    const [linkNames, setLinkNames] = useState([])
    const [showFriendly, setShowFriendly] = useState(false)
    const [expanded, setExpanded] = useState({})

    useEffect(() => {
        getObject()
    }, [objectId])

    const getObject = () => {
        axios.get(api_base+`/objects/${objectType}/${objectId}`)
          .then(response => {
            // Handle the response data
            // console.log(response)
            const dataObject = response.data.object;
            setObject(dataObject);
            // check if the dataObject has the property 'object_spec'
            if (
              dataObject.hasOwnProperty(OBJECT_SPEC_NAME) &&
              isValidObjectSpec(dataObject, dataObject[OBJECT_SPEC_NAME])
            ) {
              setObjectSpec(dataObject[OBJECT_SPEC_NAME]);
            } else {
              // if not, use default object_spec
              setObjectSpec(response.data.object_spec);
            }
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
                setExecuting(false)
                
                if (response.data.error)
                    alert(response.data.error)
                else
                    navigate(response.data.url)
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

    const exportObject = () => {
        try {
            const jsonString = JSON.stringify(object)
            const blob = new Blob([jsonString], { type: 'application/json' })
            const link = document.createElement('a')
            
            const url = URL.createObjectURL(blob)
            link.href = url
            link.download = `${object.object_id}.json`
            
            document.body.appendChild(link)
            
            link.click()
            
            document.body.removeChild(link)
            URL.revokeObjectURL(url)

        } catch (error) {
            // Handle errors
            alert(alert)
        }
        
    }

    const toggleFriendlyVersion = () => {
        setShowFriendly(prev => !prev)
    }

    const isValidRankingData = (jsonString) => {
        try {
            let obj = JSON.parse(jsonString);
            let attr = Object.keys(obj)
            if (!(attr.includes("ranking") && attr.includes("status") && attr.includes("user_id")))
                return false
            return true;
        } catch (e) {
            return false;
        }
    }

    const truncateString = (str) => {
        if (str.length > 50)
          return str.substring(0, 50) + '...'
        else
          return str
    }

    const handleToggleExpand = (propName) => {
        setExpanded(prev => {
            let newExpanded = {...prev}
            newExpanded[propName] = !newExpanded[propName]
            return newExpanded
        })
    }

    return (
        <div>
            { loading ? 
                <p>Loading...</p>
                :
                <div>
                    <div className="header">
                        {/* Only show icon if it exists */}
                        <div className="object-icon">
                            {objectType && (
                                <img
                                    src={`/static/images/${objectType}.png`}
                                    alt={`${objectType} Logo`}
                                    onError={(e) => {
                                        e.target.style.display = 'none';
                                    }}
                                />
                            )}
                        </div>
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
                            { objectType === "review"  &&
                                <button className="button spaced-button button-tertiary" onClick={toggleFriendlyVersion}> 
                                    { showFriendly ? "Back to Normal Display" : "See Friendly Version"}
                                </button>
                            }
                            <Link className="button spaced-button" to={`/${objectType}/${objectId}/edit`}  >
                                <i className="fa-solid fa-pen-to-square"></i> Edit
                            </Link>
                            <button className="button spaced-button button-secondary" onClick={cloneObject} >
                                <i className="fa-solid fa-clone"></i> Clone
                            </button>
                            { (objectType === "hypothesis" || objectType === "dataset") &&
                                <button className="button spaced-button button-tertiary" onClick={exportObject} >
                                    <i className="fa-solid fa-file-export"></i> Export
                                </button>
                            }
                            <button className="button spaced-button button-danger" onClick={deleteObject} >
                                <i className="fa-solid fa-trash-can"></i> Delete
                            </button>
                        </div>
                    </div>
                    <div className="main-content">
                    {object && objectSpec && objectSpec.properties ? (
                        <>
                            {showFriendly ? (
                                <>
                                    { isValidRankingData(object["ranking_data"]) ?
                                        <HypothesisList
                                            viewOnly
                                            runId={object["analysis_run_id"]}
                                            analysisRuns={[]} 
                                            user={{object_id: JSON.parse(object["ranking_data"]).user_id}} 
                                            savedRankings={[{analysis_run_id: object["analysis_run_id"], ...JSON.parse(object["ranking_data"])}]} 
                                            setReload={()=>{}}  
                                        />
                                    :
                                        <p>Ranking Information is not present or in the correct JSON format.</p>
                                    }
                                </>
                                
                            ) : (
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
                                                {propSpec.view === "json_tree" ? (
                                                    <JsonTreeView 
                                                        data={object[propName]} 
                                                        initialExpanded={true}
                                                    />
                                                ) : propSpec.view === "scrolling_table" ? (
                                                    <DataViewer data={object[propName]} />
                                                ) : propSpec.view === "judgment_space_visualizations" ? (
                                                    <div>
                                                      {object[propName]?.reduced_dim_plot && (
                                                        <div>
                                                          <h3>Reduced Dimensionality Plot</h3>
                                                          <SimpleSVGViewer 
                                                            svgString={object[propName].reduced_dim_plot} 
                                                            maxWidth="800px" 
                                                            maxHeight="600px"
                                                          />
                                                        </div>
                                                      )}
                                                      {object[propName]?.heatmap && (
                                                        <div>
                                                          <h3>Heatmap</h3>
                                                          <SimpleSVGViewer 
                                                            svgString={object[propName].heatmap} 
                                                            maxWidth="800px" 
                                                            maxHeight="600px"
                                                          />
                                                        </div>
                                                      )}
                                                    </div>
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
                                                ) : (propSpec.collapsible && object[propName] && object[propName].length > 50) ?  (
                                                    <div>
                                                        <button className="button" style={{backgroundColor: "grey"}} onClick={()=>handleToggleExpand(propName)}>
                                                            {expanded[propName] ? <><i className="fa-solid fa-minus"></i>  Collapse</> : <><i className="fa-solid fa-arrows-up-down"></i>  Expand</>}
                                                        </button>
                                                        <pre className='pre-format' style={{ maxWidth: "800px" }}>
                                                            {expanded[propName] ? object[propName] : truncateString(object[propName])}
                                                        </pre>
                                                    </div>
                                                    
                                                ) : propSpec.view === "markdown" || propName === "markdown" ? (
                                                    <MarkdownDisplay 
                                                        content={object[propName]} 
                                                        style={{ maxWidth: "800px"}}
                                                        className="markdown-content"
                                                    />
                                                ) : (
                                                    <MarkdownDisplay 
                                                        content={object[propName]} 
                                                        style={{ maxWidth: "800px"}}
                                                    />
                                                )}
                                                </td>
                                            </tr>
                                            )
                                        )}
                                    </tbody>
                                </table>
                            )}
                        </>
                    ) : (
                        <p>No properties available.</p>
                    )}
                    </div>
                </div>
            }
        </div>
       
    )
}

const isValidObjectSpec = (object, objectSpec) => {
    if (objectSpec.hasOwnProperty("properties")) {
      Object.entries(objectSpec.properties).forEach(([propName, propSpec]) => {
        if (!propSpec.hasOwnProperty("view")) {
          return false;
        }
        if (!object.hasOwnProperty(propName)) {
          return false;
        }
      });
      return true;
    }
    return false;
};

export default ObjectView
