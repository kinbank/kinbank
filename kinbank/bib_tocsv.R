# /usr/bin/Rscript

# convert bib file to csv
library(bib2df)
library(stringr)

sources = bib2df::bib2df('kinbank/kinbank/cldf/sources.bib')


last_names = sapply(sources$AUTHOR, function(x) gsub("^(.*?),.*", "\\1", x))
years = str_extract(sources$YEAR, "[0-9]{4}") %>% 
  ifelse(is.na(.), 'n.d.', .)

display_names = rep(NA, length(last_names))
for(i in 1:length(last_names)){
  ln = last_names[[i]]
  if(length(ln) >= 3)
    display_names[i] = paste0(ln[1], " et al. ", years[i])
  if(length(ln) == 2)
    display_names[i] = paste0(ln[1], " & ", ln[2], " ", years[i])
  if(length(ln) == 1)
    display_names[i] = paste0(ln[1]," ", years[i])
}

sources$DISPLAY = display_names
sources$AUTHOR = sapply(sources$AUTHOR, function(x) paste0(x, collapse = "; "))
sources$EDITOR = sapply(sources$EDITOR, function(x) paste0(x, collapse = "; "))

write.csv(sources, 'kinbank/kinbank/cldf/sources.csv', row.names = FALSE)
