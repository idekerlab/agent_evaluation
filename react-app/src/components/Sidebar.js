import { NavLink } from 'react-router-dom'

const Sidebar = ({objectTypes, ...props}) => {
    return (
      <div className="sidebar">
        <NavLink to={`/`} key={`home-navbtn`}>
            <button className='button'>
              home
            </button>
        </NavLink>
        {objectTypes.map((type, index) => (
            <NavLink to={`/${type}`} key={`${index}-navbtn`}>
              <button className='button'>
                {type}
              </button>
          </NavLink>
        ))}
      </div>
    )
}

export default Sidebar