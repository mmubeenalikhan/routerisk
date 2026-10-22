import { useEffect, useState } from "react";
import { Autocomplete, TextField, Typography } from "@mui/material";
import { searchPlaces } from "../api";

const SEARCH_DELAY_MS = 300;
const MIN_SEARCH_LENGTH = 3;

const placeLabel = place => (typeof place === "string" ? place : place.label);

export default function PlaceInput({ label, value, onChange }) {
  const [text, setText] = useState(placeLabel(value));
  const [options, setOptions] = useState([]);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    if (!searching) return;
    const controller = new AbortController();
    const timer = setTimeout(() => {
      searchPlaces(text, controller.signal)
        .then(places => {
          setOptions(places);
          setSearching(false);
        })
        .catch(() => {});
    }, SEARCH_DELAY_MS);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [text, searching]);

  function handleTyping(_, newText, reason) {
    setText(newText);
    if (reason !== "input") return;
    onChange(newText);
    setOptions([]);
    setSearching(newText.length >= MIN_SEARCH_LENGTH);
  }

  return (
    <Autocomplete
      freeSolo
      options={options}
      filterOptions={places => places}
      getOptionLabel={placeLabel}
      getOptionKey={place => place.id}
      isOptionEqualToValue={(place, current) => place.id === current.id}
      value={value}
      inputValue={text}
      onInputChange={handleTyping}
      onChange={(_, place) => onChange(place ?? "")}
      renderOption={({ key, ...props }, place) => (
        <li key={key} {...props}>
          <div>
            {place.label}
            <Typography variant="caption" color="text.secondary" sx={{ display: "block" }}>
              {place.kind}
            </Typography>
          </div>
        </li>
      )}
      renderInput={params => (
        <TextField
          {...params}
          label={label}
          placeholder="City, State"
          size="small"
          required
          helperText="Select a suggestion or enter a full name."
        />
      )}
    />
  );
}
