/** Client-side CSV / text export helpers for partner reports. */

function downloadBlob(filename: string, content: string, mime: string) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function csvEscape(value: string | number | null | undefined): string {
  const raw = value == null ? '' : String(value);
  if (/[",\n]/.test(raw)) {
    return `"${raw.replace(/"/g, '""')}"`;
  }
  return raw;
}

export function exportRowsAsCsv(
  filename: string,
  headers: string[],
  rows: Array<Array<string | number | null | undefined>>,
) {
  const lines = [
    headers.map(csvEscape).join(','),
    ...rows.map((row) => row.map(csvEscape).join(',')),
  ];
  downloadBlob(filename, `\uFEFF${lines.join('\n')}`, 'text/csv;charset=utf-8');
}

export function exportTextReport(filename: string, body: string) {
  downloadBlob(filename, body, 'text/plain;charset=utf-8');
}
