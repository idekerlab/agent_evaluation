import { useState, useEffect, useCallback, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { AgGridReact } from 'ag-grid-react'
import ObjectView from './ObjectView'

const api_base = process.env.REACT_APP_API_BASE_URL
const EXAMPLE_QUERIES = [
  { label: "object_id LIKE \'%55%\'", value: "object_id LIKE '%55%'" },
  { label: "properties ->> \'name\' LIKE \'%RAS%\'", value: "properties ->> 'name' LIKE '%RAS%'" },
]

const ObjectList = ({objectType, ...props}) => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [objectSpec, setObjectSpec]= useState({})
  const [checkedObjects, setCheckedObjects] = useState([])
  const [searchQuery, setSearchQuery] = useState("")
  const [rowData, setRowData] = useState([])
  const [targetId, setTargetId] = useState(""); // State to hold selected row data
  const [panelExpanded, setPanelExpanded] = useState(false); // State to manage panel collapse
  const gridRef = useRef()
  
  const colKeys = Object.keys(objectSpec).length> 0 ? Object.keys(objectSpec.properties) : []
  colKeys.splice(1, 0, "created")
  colKeys.splice(2, 0, "id")

  const colDefs = colKeys.map((key) => {
    if (key == "name") {
      return ({
        field: "name",
        filter: "agTextColumnFilter",
        headerCheckboxSelection: true,
        headerCheckboxSelectionFilteredOnly: true,
        checkboxSelection: true,
        showDisabledCheckboxes: true,
        filterParams: {
          buttons: ["reset", "apply"],
          closeOnApply: true
        },
        filterValueGetter: props => {
          return props.data.name.name
        },
        cellRenderer: props => (
          <Link to={`/${objectType}/${props.value.object_id}`}>{props.value.name || 'none'}</Link>
        )
      })
    }
    return {
      field: key, 
      filter: true,  
      filterParams: {
        buttons: ["reset", "apply"],
        closeOnApply: true
      }
    }
  })


  useEffect(() => {
      getObjects()
      clearFilters()
      setPanelExpanded(false)
  }, [objectType])


  const getObjects = (query = "") => {
    const params = {}
    params["query"] = query
    axios.get(api_base+`/objects/${objectType}`, {params})
      .then(response => {
        // Handle the response data
        const objects = response.data.objects ?? []
        setObjectSpec(response.data.object_spec ?? {})
        updateRowData(objects)
        setLoading(false)
      })
      .catch(error => {
        // Handle any errors
        alert(error)
        setLoading(false)
      })
  }


  const updateRowData = (objs) => {

    let newRowData = objs.map((obj) => {
      let newRow = {}
      Object.keys(obj.properties).map((key)=> {
        const value = obj.properties[key]
        if (key == "name") {
          newRow[key] = {object_id: obj.object_id, name: obj.properties.name}
        } else {
          newRow[key] = value
        }
      })

      if (newRow.name == null) {
        newRow['name'] = {object_id: obj.object_id, name: "none"}
      }

      newRow['id'] = obj.object_id
      return newRow
    })
    setRowData(newRowData)
  }

  const handleSearch = () => {
    if (!searchQuery.trim()) {
      getObjects()
      return
    }
    
    getObjects(searchQuery)
  }

  const handleExampleSelect = (e) => {
    setSearchQuery(e.target.value)
  }

  const clearFilters = useCallback(() => {
    if (gridRef.current)
      gridRef.current.api.setFilterModel(null)
  }, [])

  const deleteCheckedObjects = async () => {

    if (window.confirm(`Are you sure you want to delete ${checkedObjects.length} objects?`)) {
      try {
        // Map the checkedObjects array to an array of promises
          const deletePromises = checkedObjects.map(node => {
            let objId = node.data.name.object_id

            return axios.post(`${api_base}/objects/${objectType}/${objId}/delete`)
          }
        )

        // Wait for all deletion requests to complete
        const responses = await Promise.all(deletePromises)

        // Clear checked objects and refresh the objects list
        checkedObjects.map(node => {
          node.setSelected(false)
        })
        setCheckedObjects([])
        getObjects()
      } catch (error) {
          // Handle any errors that occur during the deletion process
          alert(error)
      }
    }
  }

  const onSelectionChanged = useCallback(
    (event) => {
      let nodes = event.api.getSelectedNodes()
      setCheckedObjects(nodes)
    },
    [window],
  );

  const onRowClicked = (event) => {
    setTargetId(event.data.id)
    setPanelExpanded(true)
  };

  const onGridSizeChanged = useCallback(
    (params) => {
      params.api.resetRowHeights(); // Ensures row height remains unchanged
    },
    []
  );

  return (
    <div className='main-content' style={{display: 'flex',height: '90vh', flexDirection:'column'}}>
      <div className="object-list-header" style={{ display: 'flex', height: '15vh' }}>
      <h1>{objectType === 'hypothesis' ? 'hypotheses' : `${objectType}s`}</h1>
      { "documentation" in objectSpec &&
        <p>{objectSpec.documentation}</p>
      }
      
      <button
        className="button spaced-button button-success"
        onClick={() => navigate(`/${objectType}/new`)}
      >
        <i className="fa-solid fa-plus"></i> New {objectType}
      </button>
      { (objectType == "hypothesis" || objectType === "dataset") && 
      // Only hypotheses and datasets can be exported at this time
      // ** this also needs conditional handling in the App.js component **
        <button
          className="button spaced-button button-secondary"
          onClick={() => navigate(`/${objectType}/import`)}
        >
          <i className="fa-solid fa-file-import"></i> Import {objectType}
        </button>
      }
      <button
        className="button spaced-button button-danger"
        onClick={deleteCheckedObjects}
      >
        <i className="fa-solid fa-trash-can"></i> Delete
      </button>
      </div>

      {/* Search Bar */}
      <div className="search-container" style={{ display: 'flex', height: '5vh' ,marginBottom: '1rem'}}>
        <input
          type="text"
          placeholder="Enter SQL WHERE clause"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />

        {/* Dropdown with quick example queries */}
        <select 
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="dropdown-quick-search"
        >
          <option disabled value="">
            Quick Search
          </option>
          {EXAMPLE_QUERIES.map((item) => (
            <option key={item.value} value={item.value}>
              {item.label}
            </option>
          ))}
        </select>

        <button onClick={handleSearch} className="button button-primary">
          <i className="fa-solid fa-search"></i> Search
        </button>
      </div>

      { loading ? 
        <p>Loading...</p>
        :
        rowData.length > 0 ? (
          <div className="ag-theme-quartz" style={{ display: 'flex', height: '70vh' }}>
            {/* Left Side: Ag-Grid */}
            <div style={{ flex: 1 }}>
              <AgGridReact
                ref={gridRef}
                rowSelection="multiple"
                onSelectionChanged={onSelectionChanged}
                rowData={rowData}
                columnDefs={colDefs}
                paginationPageSize={50}
                onRowClicked={onRowClicked}
                pagination={true}
                onGridSizeChanged={onGridSizeChanged}
                suppressColumnVirtualisation={true} // Ensures all columns are accessible in scroll
                gridStyle={{ width: '100%', height: '100%', overflowX: 'auto', overflowY:'auto' }} // Enables scrolling
                getRowHeight={() => 40} // Fixes row height
              />
            </div>
  
            {/* Right Side: Panel */}
            { panelExpanded && (
              <div 
                className="panel" 
                style={{ 
                  flex: 1, 
                  backgroundColor: '#f0f0f0', 
                  overflowY: 'hidden',
                  overflowX: 'hidden',
                  maxWidth: '50%',
                  position: 'relative'
                }}
              >
                <button 
                  onClick={() => setPanelExpanded(false)} 
                  style={{
                    position: 'absolute',
                    top: '5px',
                    left: '5px', 
                    zIndex: 10,
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    fontSize: '1.2rem'
                  }}
                >
                  <i className="fa-solid fa-angle-right"></i> 
                </button>

                <div style={{ 
                  width: '100%', 
                  height: '100%', 
                  overflow: 'auto'
                }}>
                  <ObjectView specs={{}} objectType={objectType} targetId={targetId} />
                </div>
              </div>
          )}
          </div>
        ) : (
          <p>No {objectType} objects to display. Try adding a new one.</p>
        )}
      </div>
  )
}

export default ObjectList