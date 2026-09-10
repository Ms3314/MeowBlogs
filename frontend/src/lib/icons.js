// Compatibility shim so the documented FontAwesome syntax
// `byPrefixAndName.fas['cat']` works without pulling the entire icon set
// (which would add ~1.5 MB to the bundle). Add to `fas` as needed.
import { faCat, faPaw, faFish } from '@fortawesome/free-solid-svg-icons'

const fas = {
  cat: faCat,
  paw: faPaw,
  fish: faFish,
}

export const byPrefixAndName = { fas }
