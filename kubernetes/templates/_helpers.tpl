{{- define "monitor.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "monitor.fullname" -}}
{{- include "monitor.name" . }}-{{ .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
