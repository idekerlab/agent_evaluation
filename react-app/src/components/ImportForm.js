import { useNavigate } from "react-router-dom"
import { api_base } from "../helpers/constants"
import axios from 'axios'

const ImportForm = ({objectType, specs, ...props}) => {
    const navigate = useNavigate()

    const handleSubmit = async (e) => {
        e.preventDefault();
    
        const form = e.target
        const formData = new FormData(form)

        try {
            let res = await axios.post(`${api_base}/objects/${objectType}/import`, formData)
            navigate(`/${objectType}/${res.data.object_id}`)
        } catch (error) {
            alert(error)
        }
        

    }

    return (
        <div>
            <div className="header">
                <h1>Import {objectType}</h1>
            </div>
            <div className="main-content">
                <form method="post" encType="multipart/form-data" id="form" onSubmit={handleSubmit}>
                    <table>
                        <tbody>
                            <tr>
                                <td style={{border: 'none'}}>
                                    <div>
                                        <label>Upload JSON: </label>
                                        <input type="file" name="json" accept=".json" />
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                    <button type="submit" className="button">Submit</button>
                </form>
            </div>
        </div>
        
    )
}

export default ImportForm