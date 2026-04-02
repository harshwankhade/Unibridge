/**
 * parseJWT(token)
 * Decodes the payload section of a JWT without verifying the signature.
 * Returns the parsed object, or null on any failure.
 */
const parseJWT = (token) => {
  try {
    const payload = token.split(".")[1];
    return JSON.parse(atob(payload));
  } catch {
    return null;
  }
};

export default parseJWT;
