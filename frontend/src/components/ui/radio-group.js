import * as React from "react"

const RadioGroup = ({ value, onValueChange, children, className, ...props }) => {
  return (
    <div className={className} {...props}>
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child, {
            checked: child.props.value === value,
            onChange: () => onValueChange(child.props.value)
          })
        }
        return child
      })}
    </div>
  )
}

const RadioGroupItem = ({ value, id, checked, onChange, className, ...props }) => {
  return (
    <input
      type="radio"
      id={id}
      value={value}
      checked={checked}
      onChange={onChange}
      className={`h-4 w-4 text-blue-600 ${className}`}
      {...props}
    />
  )
}

export { RadioGroup, RadioGroupItem }